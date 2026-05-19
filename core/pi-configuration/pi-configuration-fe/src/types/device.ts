/**
 * Device Status - Discriminated union type for different device states
 */
export type DeviceStatus =
  | {
      case: 'UNPROVISIONED';
    }
  | {
      case: 'PROVISIONED';
      mac_address: string;
      home_object_id: string;
    };

/**
 * Device Interface
 * Represents a device with its metadata and status
 */
export interface Device {
  id: string;
  name: string;
  creation_date: string;
  device_status: DeviceStatus;
}
