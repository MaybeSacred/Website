<script setup lang="ts">
import WelcomeItem from './WelcomeItem.vue'
import DocumentationIcon from './icons/IconDocumentation.vue'
import PiPicoConfiguration from './PiPicoConfiguration.vue'
import BarChart from './Chart.vue';
import { ref } from 'vue';
import type { Device } from '@/types/device';

interface MeasurementData {
  "cpu_temperature": number,
  "temperature": number,
  "humidity": number,
  "moisture": number
}
const data = ref<MeasurementData | null>(null);

const devices = ref<Device[]>([]);

const formData = ref({
  ipAddress: "192.168.1.231",
  exists: false
});

const getDevices = async () => {
  formData.value.exists = false;
  const response = await fetch(`http://192.168.1.193:8000/devices`, {
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
  <WelcomeItem>
    <template #icon>
      <DocumentationIcon />
    </template>
    <template #heading>Pi Data</template>
    <div>
      <p>CPU Temperature: {{ data?.cpu_temperature }}°C</p>
      <p>Temperature: {{ data?.temperature }}°C</p>
      <p>Humidity: {{ data?.humidity }}%</p>
      <p>Moisture: {{ data?.moisture }}%</p>
    </div>
    <a href="javascript:void(0)" @click="refreshData">Refresh</a>.
  </WelcomeItem>
  <BarChart :devices="devices" />
  <form @submit.prevent="refreshData">
    <div>
      <span>IP Address</span>
      <input type="text" v-model="formData.ipAddress" />
    </div>
    <button type="submit">Update</button>
  </form>
  <div>
    <h2>Devices</h2>
    <ul>
      <li v-for="device in devices.filter(s => s.device_status.case === 'PROVISIONED')" :key="device.id">
        {{ device.name }} - {{ (device.device_status as { mac_address: string }).mac_address }}
      </li>
    </ul>
  </div>
  <PiPicoConfiguration :ip-address="formData.ipAddress" :exists="formData.exists" />
</template>
