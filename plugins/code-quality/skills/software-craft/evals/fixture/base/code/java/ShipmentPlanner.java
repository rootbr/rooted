package shipping;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/** Plans the delivery runs that leave the depot each day. */
public class ShipmentPlanner {
    private final GeoPoint depot;
    private final String trackingPortal;

    public ShipmentPlanner(GeoPoint depot, String trackingPortal) {
        this.depot = depot;
        this.trackingPortal = trackingPortal;
    }

    List<Shipment> dueOn(List<Shipment> shipments, LocalDate day) {
        List<Shipment> dueShipments = new ArrayList<>();
        for (Shipment shipment : shipments) {
            if (shipment.promisedDate().equals(day)) {
                dueShipments.add(shipment);
            }
        }
        return dueShipments;
    }
}
