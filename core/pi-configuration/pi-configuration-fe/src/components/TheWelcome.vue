<script setup lang="ts">
import { BButton, BFormGroup, BFormInput } from 'bootstrap-vue-next'
import PiPicoConfiguration from './PiPicoConfiguration.vue'
import BarChart from './Chart.vue';
import { ref } from 'vue';
import type { Device } from '@/types/device';
import MapView from './MapView.vue';

interface MeasurementData {
  "cpu_temperature": number,
  "temperature": number,
  "humidity": number,
  "moisture": number
}
const data = ref<MeasurementData | null>(null);

const devices = ref<Device[]>([]);
const deviceProvisioned = (device: Device) => {
  const index = devices.value.findIndex(existing => existing.id === device.id);
  devices.value = index === -1
    ? [...devices.value, device]
    : devices.value.map(existing => existing.id === device.id ? device : existing);
};

const formData = ref({
  ipAddress: "192.168.1.231",
  exists: false
});

const getDevices = async () => {
  formData.value.exists = false;
  const response = await fetch(`http://localhost:8000/devices/`, {
    method: 'GET',
  });
  const json: Device[] = await response.json();
  devices.value = json.filter(device => device.device_status.case === 'PROVISIONED');
}

const refreshData = () => {
  const controller = new AbortController();
  const signal = controller.signal;
  formData.value.exists = false;
  fetch(`http://${formData.value.ipAddress}/measurement`, {
    method: 'GET',
    signal
  })
    .then(res => res.json())
    .then(json => {
      data.value = json;
      formData.value.exists = true;
    })
    .catch(() => {
      formData.value.exists = false;
    });
  setTimeout(() => {
    controller.abort();
  }, 5000);
}

refreshData();
getDevices();
</script>

<template>
  <h2 class="h4">Pi Data</h2>
  <div class="border rounded p-3 mb-3">
    <p>CPU Temperature: {{ data?.cpu_temperature }}°C</p>
    <p>Temperature: {{ data?.temperature }}°C</p>
    <p>Humidity: {{ data?.humidity }}%</p>
    <p>Moisture: {{ data?.moisture }}%</p>
  </div>
  <BButton type="button" variant="outline-primary" size="sm" class="mb-3" @click="refreshData">Refresh</BButton>
  <MapView @device-provisioned="deviceProvisioned" />
  <BarChart :devices="devices" />
  <form class="my-3" @submit.prevent="refreshData">
    <BFormGroup label="IP Address" label-for="measurement-ip" class="mb-3">
      <BFormInput id="measurement-ip" v-model="formData.ipAddress" />
    </BFormGroup>
    <BButton type="submit" variant="primary">Update</BButton>
  </form>
  <div>
    <h2 class="h4">Devices</h2>
    <ul class="list-group mb-3">
      <li v-for="device in devices.filter(s => s.device_status.case === 'PROVISIONED')" :key="device.id" class="list-group-item">
        {{ device.name }} - {{ (device.device_status as { mac_address: string }).mac_address }}
      </li>
    </ul>
  </div>
  <PiPicoConfiguration :ip-address="formData.ipAddress" :exists="formData.exists" />
</template>
