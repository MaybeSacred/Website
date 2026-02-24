<script setup lang="ts">
import WelcomeItem from './WelcomeItem.vue'
import DocumentationIcon from './icons/IconDocumentation.vue'
import PiPicoConfiguration from './PiPicoConfiguration.vue'
import BarChart from './Chart.vue';
import { ref } from 'vue';

interface WelcomeItem {
  "cpu_temperature": number,
  "temperature": number,
  "humidity": number,
  "moisture": number
}
const data = ref<WelcomeItem | null>(null);
const formData = ref({
  ipAddress: "192.168.1.231",
  exists: false
});

const refreshData = () => {
  const controller = new AbortController();
  const signal = controller.signal;
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
  <BarChart />
  <form @submit.prevent="refreshData">
    <div>
      <span>IP Address</span>
      <input type="text" v-model="formData.ipAddress" />
    </div>
    <button type="submit">Update</button>
  </form>
  <PiPicoConfiguration :ip-address="formData.ipAddress" :exists="formData.exists" />
</template>
