import sys
from flync import LinBusConfig, MasterNode, SlaveNode, ScheduleTable
from pydantic import ValidationError

lin_bus_config = LinBusConfig(
    master_node=MasterNode(node_id="NODE_1", node_type="MASTER"),
    slave_nodes=[SlaveNode(node_id="NODE_2", node_type="SLAVE")],
    frames=[
        {"frame_id": "FRAME_1", "data_rate": 10},
        {"frame_id": "FRAME_2", "data_rate": 20}
    ],
    schedule_tables=[
        ScheduleTable(
            table_name="TABLE_1",
            frame_references=["FRAME_1", "FRAME_2"]
        )
    ]
)

print("SUCCESS")
sys.exit(0)