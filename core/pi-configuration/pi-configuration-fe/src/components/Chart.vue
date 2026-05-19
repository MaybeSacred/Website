<script setup lang="ts">
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  type ChartData,
  TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Line } from 'vue-chartjs'
import type { Device } from '@/types/device';
import { computed, ref, watch } from 'vue';

ChartJS.register(Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  TimeScale);

const props = defineProps({
  devices: Array<Device>
});

interface EnvironmentSensorData {
  case: 'ENVIRONMENT_SENSOR'
  mac_address: string
  source_date: string
  cpu_temperature: number | null
  temperature: number | null
  distance: number | null
  humidity: number | null
  lux: number | null
  pressure: number | null
  uv: number | null
  gas: number | null
  water_depth_raw: number | null
  moisture_percent: number | null
}

interface Envelope {
  id: string
  date: string
  data: EnvironmentSensorData
}

const chartData = ref<ChartData<"line", [Date, number][], unknown>>({
  //labels: ['January', 'February', 'March'],
  datasets: [{
    data: [],
    label: 'Temperature (°C)',
    fill: false,
    borderColor: 'rgb(75, 192, 192)'
  }]
});

const macAddressLookup: Record<string, [string, string]> = {
  '88:a2:9e:13:2c:38': ['rgb(120, 40, 20)', 'rgb(40, 120, 60)'],
  '2c:cf:67:f7:33:9c': ['rgb(170, 40, 20)', 'rgb(40, 170, 40)'],
  '88:a2:9e:12:c6:06': ['rgb(220, 40, 20)', 'rgb(40, 220, 20)']
}

const colorStringFromMac = (macAddress: string) => {
  const hash = macAddress.split(':').slice(3, 6).map((part) => Number.parseInt(part, 16));
  const r = (hash[0]!) % 128 + 128;
  const g = (hash[1]!) % 128 + 128;
  const b = (hash[2]!) % 128 + 128;
  return `rgb(${r}, ${g}, ${b})`;
}

const transformedData = ref<Record<string, [date: Date, temperature: number, humidity: number][]>>({});

const fetchAndUpdate = async (macAddress: string) => {
  const data = await fetch(`http://192.168.1.193:8000/data-ingestion/${macAddress}?min_hours_ago=0&max_hours_ago=72`)
  const envelop: Envelope[] = await data.json()
  const dataWithDate =
    envelop
      .map(entry => ({ ...entry, date: new Date(entry.date + 'Z') }))
      .sort((a, b) => a.date.getTime() - b.date.getTime());
  const minDate = dataWithDate[0]?.date || new Date();
  transformedData.value = {
    ...transformedData.value,
    [macAddress]: dataWithDate.map(entry => [entry.date, entry.data.temperature ?? 0, entry.data.humidity ?? 0])
  };
  chartData.value = {
    //labels: dataWithDate.map(entry => entry.date.toLocaleString()),
    // labels: [...new Array(144).keys()]
    //   .map(entry => {
    //     const newDate = new Date(minDate.getTime() + entry * 60 * 60 * 1000);
    //     return new Date(newDate.getFullYear(), newDate.getMonth(), newDate.getDate(), newDate.getHours(), 0, 0).toLocaleString();
    //   }),
    datasets: Object.entries(transformedData.value).flatMap(([macAddress, dataWithDate]) => [
      {
        data: dataWithDate.map(entry => [entry[0], entry[1]]),
        label: 'Temperature (°C) - ' + macAddress,
        fill: false,
        borderColor: colorStringFromMac(macAddress),
        tension: 0.1
      },
      {
        data: dataWithDate.map(entry => [entry[0], entry[2]]),
        label: 'Humidity (%) - ' + macAddress,
        fill: false,
        borderColor: colorStringFromMac(macAddress),
        tension: 0.1
      }
    ])
  };
}

const chartOptions = computed(() => ({
  responsive: true,
  scales: {
    x: {
      type: 'time' as const,
      time: {
        unit: 'hour' as const,
        tooltipFormat: 'dd MMM yyyy, HH:mm',
        displayFormats: {
          hour: 'dd MMM yyyy, HH:mm'
        }
      },
      title: {
        display: true,
        text: 'Date'
      }
    }
  }
}));

watch( () => props.devices, (newDevices, oldDevices)=> {
  console.log("Props changed:", newDevices, oldDevices);
  if (newDevices) {
    newDevices?.forEach(device => fetchAndUpdate((device.device_status as { mac_address: string }).mac_address));
  }
});

</script>

<template>
  <Line :data="(chartData as unknown as ChartData<'line', (number)[], unknown>)" :options="chartOptions" />
</template>
