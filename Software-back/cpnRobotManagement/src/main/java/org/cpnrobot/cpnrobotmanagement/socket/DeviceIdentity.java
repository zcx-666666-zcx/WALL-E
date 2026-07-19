package org.cpnrobot.cpnrobotmanagement.socket;

public final class DeviceIdentity {

    public static final String STANDARD_DEVICE_ID = "WALLE_1";
    public static final String LEGACY_DEVICE_ID = "WALEE_1";

    private DeviceIdentity() {
    }

    public static String canonicalize(String deviceId) {
        if (deviceId == null) {
            return "";
        }
        String value = deviceId.trim();
        if (STANDARD_DEVICE_ID.equalsIgnoreCase(value)
                || LEGACY_DEVICE_ID.equalsIgnoreCase(value)) {
            return STANDARD_DEVICE_ID;
        }
        return value;
    }

    public static String canonicalizeRoom(String room) {
        if (room == null) {
            return "";
        }
        String value = room.trim();
        String prefix = "robot_";
        if (!value.startsWith(prefix)) {
            return value;
        }
        return prefix + canonicalize(value.substring(prefix.length()));
    }
}
