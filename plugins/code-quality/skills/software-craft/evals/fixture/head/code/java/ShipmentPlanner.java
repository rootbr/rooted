package shipping;

import java.time.Duration;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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
            if (shipment.promisedDate().equals(day) && !shipment.isCancelled()) {
                dueShipments.add(shipment);
            }
        }
        return dueShipments;
    }

    /** Planar distance from the depot in degrees; accurate enough to order the stops of one city run. */
    double distanceFromDepot(GeoPoint stop) {
        double x = stop.longitude() - depot.longitude();
        double y = stop.latitude() - depot.latitude();
        return Math.sqrt(x * x + y * y);
    }

    Map<String, Integer> countShipmentsByCarrier(List<Shipment> shipments) {
        Map<String, Integer> carrierMap = new HashMap<>();
        for (Shipment shipment : shipments) {
            carrierMap.merge(shipment.carrier(), 1, Integer::sum);
        }
        return carrierMap;
    }

    Notification composeDelayNotice(Shipment shipment, Duration delay) {
        String url = trackingPortal + "/track/" + shipment.trackingNumber();
        LocalDate newDate = shipment.promisedDate().plusDays(delay.toDays());
        Notification notice = new Notification(shipment.recipientEmail());
        notice.subject("Your parcel " + shipment.trackingNumber() + " is delayed");
        notice.line("Carrier: " + shipment.carrier());
        notice.line("Original delivery date: " + shipment.promisedDate());
        notice.line("New delivery date: " + newDate);
        notice.line("Reason: " + shipment.delayReason());
        notice.line("We are sorry for the wait.");
        notice.line("");
        notice.line("Follow the parcel at:");
        notice.line(url);
        return notice;
    }
}
