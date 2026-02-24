<script setup lang="ts">
import { ref } from 'vue';

interface PiConfiguration {
  general: {
    enable_dht20_sensor: boolean,
    enable_stemma_moisture_sensor: boolean,
    enable_sht30_sensor: boolean,
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


const props = defineProps({
  ipAddress: String,
  exists: Boolean
});

const currentConfiguration = ref<PiConfiguration | null>(null);

const configChanges = ref<PiConfigurationChanges>({
  general: {},
  network: {},
  logging: {}
});

const fetchConfig = () => {
  fetch(`http://${props.ipAddress}/configuration`)
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
fetchConfig();
</script>

<template>
  <div>Pi @ {{ ipAddress }}</div>
  <div v-if="!exists">No configuration found for this IP address.</div>
  <div v-if="exists">
    <div><span>Version: {{ currentConfiguration?.version }}</span></div>
    <form @submit.prevent="postConfig">
      <div v-if="currentConfiguration">
        <div>
          <h4>General Configuration</h4>
          <div>
            <span>Measurement Interval:</span>
            <input v-model.number="configChanges.general.measurement_interval"
              :placeholder="currentConfiguration.general.measurement_interval.toString()" />
          </div>
          <div>
            <span>Heartbeat Interval:</span>
            <input v-model.number="configChanges.general.heartbeat_interval"
              :placeholder="currentConfiguration.general.heartbeat_interval.toString()" />
          </div>
          <div>
            <span>Data Write Interval:</span>
            <input v-model.number="configChanges.general.data_write_interval"
              :placeholder="currentConfiguration.general.data_write_interval.toString()" />
          </div>
          <div>
            <span>Enable DHT20 Sensor:</span>
            <input v-model="configChanges.general.enable_dht20_sensor" type="checkbox"
              :checked="currentConfiguration.general.enable_dht20_sensor" />
          </div>
          <div>
            <span>Enable SHT30 Sensor:</span>
            <input v-model="configChanges.general.enable_sht30_sensor" type="checkbox"
              :checked="currentConfiguration.general.enable_sht30_sensor" />
          </div>
          <div>
            <span>Enable Stemma Moisture Sensor:</span>
            <input v-model="configChanges.general.enable_stemma_moisture_sensor" type="checkbox"
              :checked="currentConfiguration.general.enable_stemma_moisture_sensor" />
          </div>
          <div>
            <span>Enable Moisture Temp Humidity:</span>
            <input v-model="configChanges.general.enable_moisture_temp_humidity" type="checkbox"
              :checked="currentConfiguration.general.enable_moisture_temp_humidity" />
          </div>
          <h4>Network Configuration</h4>
          <div>
            <span>Network SSID:</span>
            <input v-model="configChanges.network.network_ssid" type="text"
              :placeholder="currentConfiguration.network.network_ssid" />
          </div>
          <div>
            <span>Ingestion Server URL:</span>
            <input v-model="configChanges.network.ingestion_server_url" type="text"
              :placeholder="currentConfiguration.network.ingestion_server_url" />
          </div>
          <div>
            <span>Ingestion Server Port:</span>
            <input v-model.number="configChanges.network.ingestion_server_port" type="number"
              :placeholder="currentConfiguration.network.ingestion_server_port.toString()" />
          </div>
          <h4>Logging Configuration</h4>
          <div>
            <span>Enable Logging:</span>
            <input v-model="configChanges.logging.enable_logging" type="checkbox"
              :checked="currentConfiguration.logging.enable_logging" />
          </div>
          <div v-if="configChanges.logging.enable_logging === true">
            <span>Log Level:</span>
            <input v-model.number="configChanges.logging.log_level" type="number"
              :placeholder="currentConfiguration.logging.log_level.toString()" v-bind:min="1" v-bind:max="3" />
          </div>
        </div>
        <button type="submit">Save</button>
      </div>
    </form>
  </div>
</template>
