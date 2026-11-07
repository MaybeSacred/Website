<script setup lang="ts">
import { ref, watch } from 'vue';
import { BButton, BCard, BFormCheckbox, BFormGroup, BFormInput } from 'bootstrap-vue-next';

interface PiConfiguration {
  general: {
    enable_dht20_sensor: boolean,
    enable_stemma_moisture_sensor: boolean,
    enable_sht30_sensor: boolean,
    enable_sht40_sensor: boolean,
    enable_moisture_temp_humidity: boolean,
    measurement_interval: number,
    heartbeat_interval: number,
    data_write_interval: number
  },
  network: {
    ingestion_server_port: number,
    network_ssid: string,
    ingestion_server_url: string
  },
  logging: {
    enable_logging: boolean,
    log_level: number
  },
  version: string
}

type PiConfigurationChanges = {
  general: Partial<PiConfiguration["general"]>,
  network: Partial<PiConfiguration["network"]>,
  logging: Partial<PiConfiguration["logging"]>
};

const defaultConfigChanges: PiConfigurationChanges = {
  general: {},
  network: {},
  logging: {}
};

const props = defineProps({
  ipAddress: String,
  exists: Boolean
});

const currentConfiguration = ref<PiConfiguration | null>(null);
const currentRelayState = ref<boolean | null>(null);

const configChanges = ref<PiConfigurationChanges>(defaultConfigChanges);

const fetchConfig = () => {
  const controller = new AbortController();
  const signal = controller.signal;
  fetch(`http://${props.ipAddress}/configuration`, {
    method: 'GET',
    signal
  })
  .then(res => res.json())
  .then(json => {
    currentConfiguration.value = json;
    configChanges.value = {
      general: {},
      network: {},
      logging: { enable_logging: json.logging.enable_logging }
    };
  });
  setTimeout(() => {
    controller.abort();
  }, 5000);
};

const postConfig = () => {
  fetch(`http://${props.ipAddress}/configuration`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(configChanges.value)
  })
    .then(res => res.json())
    .then(json => {
      currentConfiguration.value = json;
      configChanges.value = {
        general: {},
        network: {},
        logging: { enable_logging: json.logging.enable_logging }
      };
    });
};

const postRelayOnOff = (on: boolean) => {
  fetch(`http://${props.ipAddress}/relay`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ on: on })
  })
    .then(res => res.json())
    .then(json => {
      currentRelayState.value = json.on;
    });
};

fetchConfig();

watch( () => [props.ipAddress, props.exists], ([newIp, newExists], [oldIp, oldExists])=> {
  console.log("Props changed:", newIp, newExists, oldIp, oldExists);
  if (newExists) {
    fetchConfig();
  } else {
    currentConfiguration.value = null;
    configChanges.value = defaultConfigChanges;
  }
});

</script>

<template>
  <BCard class="my-3">
    <h2 class="h4">Pi @ {{ ipAddress }}</h2>
    <p v-if="!exists" class="alert alert-info mb-0">No configuration found for this IP address.</p>
    <template v-if="exists">
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-3">
      <span class="text-body-secondary">Version: {{ currentConfiguration?.version }}</span>
      <BButton type="button" variant="outline-warning" @click="postRelayOnOff(!(currentRelayState ?? false))">Power Cycle</BButton>
    </div>
    <form @submit.prevent="postConfig">
      <template v-if="currentConfiguration">
        <div class="row g-4">
          <section class="col-12 col-lg-6" aria-labelledby="general-configuration-title">
          <h3 id="general-configuration-title" class="h5 border-bottom pb-2">General Configuration</h3>
          <BFormGroup label="Measurement Interval:" label-for="measurement-interval" class="mb-3">
            <BFormInput v-model.number="configChanges.general.measurement_interval"
              id="measurement-interval" :placeholder="currentConfiguration.general.measurement_interval.toString()" />
          </BFormGroup>
          <BFormGroup label="Heartbeat Interval:" label-for="heartbeat-interval" class="mb-3">
            <BFormInput v-model.number="configChanges.general.heartbeat_interval"
              id="heartbeat-interval" :placeholder="currentConfiguration.general.heartbeat_interval.toString()" />
          </BFormGroup>
          <BFormCheckbox id="enable-dht20-sensor" class="mb-2" switch
            :model-value="configChanges.general.enable_dht20_sensor ?? currentConfiguration.general.enable_dht20_sensor"
            @update:model-value="configChanges.general.enable_dht20_sensor = $event === true">Enable DHT20 Sensor</BFormCheckbox>
          <BFormCheckbox id="enable-sht30-sensor" class="mb-2" switch
            :model-value="configChanges.general.enable_sht30_sensor ?? currentConfiguration.general.enable_sht30_sensor"
            @update:model-value="configChanges.general.enable_sht30_sensor = $event === true">Enable SHT30 Sensor</BFormCheckbox>
          <BFormCheckbox id="enable-sht40-sensor" class="mb-2" switch
            :model-value="configChanges.general.enable_sht40_sensor ?? currentConfiguration.general.enable_sht40_sensor"
            @update:model-value="configChanges.general.enable_sht40_sensor = $event === true">Enable SHT40 Sensor</BFormCheckbox>
          <BFormCheckbox id="enable-stemma-moisture-sensor" class="mb-2" switch
            :model-value="configChanges.general.enable_stemma_moisture_sensor ?? currentConfiguration.general.enable_stemma_moisture_sensor"
            @update:model-value="configChanges.general.enable_stemma_moisture_sensor = $event === true">Enable Stemma Moisture Sensor</BFormCheckbox>
          <BFormCheckbox id="enable-moisture-temp-humidity" class="mb-2" switch
            :model-value="configChanges.general.enable_moisture_temp_humidity ?? currentConfiguration.general.enable_moisture_temp_humidity"
            @update:model-value="configChanges.general.enable_moisture_temp_humidity = $event === true">Enable Moisture Temp Humidity</BFormCheckbox>
          </section>
          <section class="col-12 col-lg-6" aria-labelledby="network-configuration-title">
          <h3 id="network-configuration-title" class="h5 border-bottom pb-2">Network Configuration</h3>
          <BFormGroup label="Network SSID:" label-for="network-ssid" class="mb-3">
            <BFormInput v-model="configChanges.network.network_ssid" type="text"
              id="network-ssid" :placeholder="currentConfiguration.network.network_ssid" />
          </BFormGroup>
          <BFormGroup label="Ingestion Server URL:" label-for="ingestion-server-url" class="mb-3">
            <BFormInput v-model="configChanges.network.ingestion_server_url" type="text"
              id="ingestion-server-url" :placeholder="currentConfiguration.network.ingestion_server_url" />
          </BFormGroup>
          <BFormGroup label="Ingestion Server Port:" label-for="ingestion-server-port" class="mb-3">
            <BFormInput v-model.number="configChanges.network.ingestion_server_port" type="number"
              id="ingestion-server-port" :placeholder="currentConfiguration.network.ingestion_server_port.toString()" />
          </BFormGroup>
          </section>
          <section class="col-12" aria-labelledby="logging-configuration-title">
          <h3 id="logging-configuration-title" class="h5 border-bottom pb-2">Logging Configuration</h3>
          <BFormCheckbox id="enable-logging" switch class="mb-3"
            :model-value="configChanges.logging.enable_logging ?? currentConfiguration.logging.enable_logging"
            @update:model-value="configChanges.logging.enable_logging = $event === true">
            Enable Logging
          </BFormCheckbox>
          <BFormGroup v-if="configChanges.logging.enable_logging === true" label="Log Level:" label-for="log-level" class="mb-3">
            <BFormInput v-model.number="configChanges.logging.log_level" type="number"
              id="log-level" :placeholder="currentConfiguration.logging.log_level.toString()" v-bind:min="1" v-bind:max="3" />
          </BFormGroup>
          </section>
        </div>
        <BButton type="submit" variant="primary" class="mt-3">Save</BButton>
      </template>
    </form>
    </template>
  </BCard>
</template>
