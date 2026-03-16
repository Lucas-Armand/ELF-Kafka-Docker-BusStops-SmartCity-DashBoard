import time
import requests
import urllib3


class NiFiClient:
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = False):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update({"Content-Type": "application/json"})
        self._authenticate(username, password)

    def _authenticate(self, username: str, password: str):
        response = self.session.post(
            f"{self.base_url}/nifi-api/access/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )

        if response.status_code not in (200, 201):
            print("NiFi auth failed", flush=True)
            print("URL:", f"{self.base_url}/nifi-api/access/token", flush=True)
            print("Status:", response.status_code, flush=True)
            print("Headers:", dict(response.headers), flush=True)
            print("Body:", response.text[:500], flush=True)
            response.raise_for_status()

        token = response.text.strip()
        content_type = response.headers.get("Content-Type", "")

        if "html" in content_type.lower() or token.startswith("<"):
            raise RuntimeError(
                f"NiFi auth returned HTML instead of token: {token[:300]}"
            )

        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def wait_until_ready(self, timeout_seconds: int = 100, sleep_seconds: int = 5):
        deadline = time.time() + timeout_seconds

        while time.time() < deadline:
            try:
                response = self.session.get(f"{self.base_url}/nifi-api/flow/about", timeout=10)
                print(response.status_code, response.text[:500], flush=True)
                if response.status_code == 200:
                    return
            except requests.RequestException:
                pass

            time.sleep(sleep_seconds)

        raise RuntimeError("NiFi did not become ready in time")

    def create_process_group(self, parent_pg_id: str, name: str, x: float, y: float):
        payload = {
            "revision": {"version": 0},
            "component": {
                "name": name,
                "position": {"x": x, "y": y},
            },
        }
        response = self.session.post(
            f"{self.base_url}/nifi-api/process-groups/{parent_pg_id}/process-groups",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def create_processor(self, pg_id: str, processor_type: str, name: str, x: float, y: float):
        payload = {
            "revision": {"version": 0},
            "component": {
                "type": processor_type,
                "name": name,
                "position": {"x": x, "y": y},
            },
        }
        response = self.session.post(
            f"{self.base_url}/nifi-api/process-groups/{pg_id}/processors",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def get_processor(self, processor_id: str):
        response = self.session.get(f"{self.base_url}/nifi-api/processors/{processor_id}")
        response.raise_for_status()
        return response.json()

    def update_processor(self, processor_entity: dict, properties: dict, scheduling_period: str = "60 sec",  auto_terminated_relationships: list = []):
        processor_id = processor_entity["id"]
        current = self.get_processor(processor_id)

        current["component"]["config"]["properties"].update(properties)
        current["component"]["config"]["schedulingPeriod"] = scheduling_period

        if auto_terminated_relationships is not None:
            current["component"]["config"]["autoTerminatedRelationships"] = auto_terminated_relationships

        response = self.session.put(
            f"{self.base_url}/nifi-api/processors/{processor_id}",
            json=current,
        )
        response.raise_for_status()
        return response.json()

    def update_processor_state(self, processor_id: str, state: str):
        current = self.get_processor(processor_id)

        payload = {
            "revision": {"version": current["revision"]["version"]},
            "state": state,
            "disconnectedNodeAcknowledged": False,
        }
        response = self.session.put(
            f"{self.base_url}/nifi-api/processors/{processor_id}/run-status",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def create_connection(
        self,
        pg_id: str,
        source_id: str,
        source_group_id: str,
        source_type: str,
        destination_id: str,
        destination_group_id: str,
        destination_type: str,
        relationships: list[str],
    ):
        payload = {
            "revision": {"version": 0},
            "component": {
                "source": {
                    "id": source_id,
                    "groupId": source_group_id,
                    "type": source_type,
                },
                "destination": {
                    "id": destination_id,
                    "groupId": destination_group_id,
                    "type": destination_type,
                },
                "selectedRelationships": relationships,
                "bends": [],
            },
        }

        response = self.session.post(
            f"{self.base_url}/nifi-api/process-groups/{pg_id}/connections",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def create_controller_service(self, pg_id: str, service_type: str, name: str):
        payload = {
            "revision": {"version": 0},
            "component": {
                "type": service_type,
                "name": name,
            },
        }
        response = self.session.post(
            f"{self.base_url}/nifi-api/process-groups/{pg_id}/controller-services",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def get_controller_service(self, service_id: str):
        response = self.session.get(f"{self.base_url}/nifi-api/controller-services/{service_id}")
        response.raise_for_status()
        return response.json()
        
        
    def list_controller_services(self, pg_id: str):
        response = self.session.get(
            f"{self.base_url}/nifi-api/flow/process-groups/{pg_id}/controller-services"
        )
        response.raise_for_status()
        data = response.json()
        return data.get("controllerServices", [])


    def find_controller_service(self, pg_id: str, name: str, service_type: str | None = None):
        services = self.list_controller_services(pg_id)

        for service in services:
            component = service.get("component", {})
            if component.get("name") != name:
                continue
            if service_type and component.get("type") != service_type:
                continue
            return service

        return None

    def get_or_create_controller_service(self, pg_id: str, service_type: str, name: str):
        existing = self.find_controller_service(pg_id, name=name, service_type=service_type)
        if existing is not None:
            return existing
            
        return self.create_controller_service(
            pg_id=pg_id,
            service_type=service_type,
            name=name,
        )

    def update_controller_service(self, service_entity: dict, properties: dict):
        service_id = service_entity["id"]
        current = self.get_controller_service(service_id)
        current["component"]["properties"].update(properties)

        response = self.session.put(
            f"{self.base_url}/nifi-api/controller-services/{service_id}",
            json=current,
        )
        response.raise_for_status()
        return response.json()

    def update_controller_service_state(self, service_id: str, state: str):
        current = self.get_controller_service(service_id)
        payload = {
            "revision": {"version": current["revision"]["version"]},
            "state": state,
            "disconnectedNodeAcknowledged": False,
        }

        response = self.session.put(
            f"{self.base_url}/nifi-api/controller-services/{service_id}/run-status",
            json=payload,
        )
        response.raise_for_status()
        return response.json()



def create_http_to_kafka_pipeline(
    client: NiFiClient,
    parent_pg_id: str,
    process_group_name: str,
    remote_url: str,
    kafka_topic_raw: str,
    kafka_topic_dlq: str,
    kafka_bootstrap: str,
    api_key: str = "",
):
    process_group = client.create_process_group(
        parent_pg_id=parent_pg_id,
        name=process_group_name,
        x=400.0,
        y=200.0,
    )
    pg_id = process_group["id"]
    
    
    kafka_connection_service = client.get_or_create_controller_service(
        pg_id=pg_id,
        service_type="org.apache.nifi.kafka.service.Kafka3ConnectionService",
        name="Kafka3ConnectionService",
    )

    kafka_connection_service = client.update_controller_service(
        kafka_connection_service,
        properties={
            "bootstrap.servers": kafka_bootstrap,
            "security.protocol": "PLAINTEXT",
            "default.api.timeout.ms": "60 sec",
            "max.block.ms": "5 sec",
            "ack.wait.time": "5 sec",
            "max.poll.records": "10000",
            "isolation.level": "read_committed",
        },
    )
    

    invoke_http = client.create_processor(
        pg_id=pg_id,
        processor_type="org.apache.nifi.processors.standard.InvokeHTTP",
        name="Invoke HTTP",
        x=100.0,
        y=100.0,
    )

    route_on_attribute = client.create_processor(
        pg_id=pg_id,
        processor_type="org.apache.nifi.processors.standard.RouteOnAttribute",
        name="Route Success",
        x=450.0,
        y=100.0,
    )

    publish_kafka_raw = client.create_processor(
        pg_id=pg_id,
        processor_type="org.apache.nifi.kafka.processors.PublishKafka",
        name="Publish Kafka",
        x=800.0,
        y=100.0,
    )
    publish_kafka_dlq = client.create_processor(
        pg_id=pg_id,
        processor_type="org.apache.nifi.kafka.processors.PublishKafka",
        name="Publish DLQ Kafka",
        x=800.0,
        y=180.0,
    )
    
    invoke_properties = {
        "HTTP URL": remote_url,
        "HTTP Method": "GET",
        "Connection Timeout": "5 secs",
        "Socket Read Timeout": "15 secs",
        "Socket Write Timeout": "15 secs",
        "Socket Idle Timeout": "5 mins",
        "Socket Idle Connections": "5",
        "Request Date Header Enabled": "True",
        "Response Body Ignored": "false",
        "Response Redirects Enabled": "True",
        "accept": "application/x-protobuf",
        "apiKey": api_key
    }

    invoke_http = client.update_processor(
        invoke_http,
        properties=invoke_properties,
        scheduling_period="30 sec",
    )

    route_on_attribute = client.update_processor(
        route_on_attribute,
        properties={
            "success": "${invokehttp.status.code:equals('200')}",
        },
        scheduling_period="0 sec",
    )

    publish_kafka_raw = client.update_processor(
        publish_kafka_raw,
        properties={
            "Topic Name": kafka_topic_raw,
            "Kafka Connection Service": kafka_connection_service["id"],
            "Transactions Enabled": "false",
        },
        scheduling_period="0 sec",
        auto_terminated_relationships=["failure", "success"],
    )

    publish_kafka_dlq = client.update_processor(
        publish_kafka_dlq,
        properties={
            "Topic Name": kafka_topic_dlq,
            "Kafka Connection Service": kafka_connection_service["id"],
            "Transactions Enabled": "false",
        },
        scheduling_period="0 sec",
        auto_terminated_relationships=["failure", "success"],
    )

    time.sleep(1)
    client.update_controller_service_state(kafka_connection_service["id"], "ENABLED")


    client.create_connection(
        pg_id=pg_id,
        source_id=invoke_http["id"],
        source_group_id=pg_id,
        source_type="PROCESSOR",
        destination_id=route_on_attribute["id"],
        destination_group_id=pg_id,
        destination_type="PROCESSOR",
        relationships=["Failure", "No Retry", "Original", "Response", "Retry"],
    )

    client.create_connection(
        pg_id=pg_id,
        source_id=route_on_attribute["id"],
        source_group_id=pg_id,
        source_type="PROCESSOR",
        destination_id=publish_kafka_raw["id"],
        destination_group_id=pg_id,
        destination_type="PROCESSOR",
        relationships=["success"],
    )

    client.create_connection(
        pg_id=pg_id,
        source_id=route_on_attribute["id"],
        source_group_id=pg_id,
        source_type="PROCESSOR",
        destination_id=publish_kafka_dlq["id"],
        destination_group_id=pg_id,
        destination_type="PROCESSOR",
        relationships=["unmatched"],
    )
    
    time.sleep(1)

    for processor in [invoke_http, route_on_attribute, publish_kafka_raw, publish_kafka_dlq]:
        client.update_processor_state(processor["id"], "RUNNING")

    return process_group
