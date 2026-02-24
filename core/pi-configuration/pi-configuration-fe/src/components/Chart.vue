  <script setup lang="ts">
  // DataPage.vue
  import { Bar } from 'vue-chartjs'
  import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
  import { computed } from 'vue';

  ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

  const chartData = computed(() => ({
    labels: ['January', 'February', 'March'],
    datasets: [{ data: [40, 20, 12] }]
  }));

  const chartOptions = computed(() => ({
    responsive: true
  }));
</script>

<template>
  <Bar :data="chartData" :options="chartOptions" />
</template>

