from xml.etree import ElementTree

from bay_area_traffic_sim.metrics import summarize_tripinfos


def test_summarize_tripinfos_averages_completed_trips() -> None:
    root = ElementTree.fromstring(
        """
        <tripinfos>
            <tripinfo id="one" duration="10" waitingTime="2" timeLoss="3"/>
            <tripinfo id="two" duration="20" waitingTime="4" timeLoss="9"/>
        </tripinfos>
        """
    )

    metrics = summarize_tripinfos(root)

    assert metrics.completed_vehicles == 2
    assert metrics.average_travel_time_seconds == 15
    assert metrics.average_waiting_time_seconds == 3
    assert metrics.average_time_loss_seconds == 6


def test_summarize_tripinfos_handles_no_completed_trips() -> None:
    metrics = summarize_tripinfos(ElementTree.fromstring("<tripinfos/>"))

    assert metrics.completed_vehicles == 0
    assert metrics.average_travel_time_seconds is None
