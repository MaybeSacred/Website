<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { BButton, BFormGroup, BFormInput, BFormSelect, BFormSelectOption } from 'bootstrap-vue-next';
import type { Device } from '@/types/device';
import type { HomeObject } from '@/types/homeObject';

const props = defineProps<{ homeObject: HomeObject }>();
const emit = defineEmits<{
  close: [];
  provisioned: [device: Device];
}>();

const dialog = ref<HTMLDialogElement | null>(null);
const devices = ref<Device[]>([]);
const deviceId = ref('');
const macAddress = ref('');
const loading = ref(false);
const saving = ref(false);
const errorMessage = ref('');

const loadDevices = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    const response = await fetch('http://localhost:8000/devices/');
    if (!response.ok) throw new Error(`Unable to load devices (HTTP ${response.status}).`);
    devices.value = await response.json();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to load devices.';
  } finally {
    loading.value = false;
  }
};

const selectDevice = () => {
  const status = devices.value.find(device => device.id === deviceId.value)?.device_status;
  macAddress.value = status?.case === 'PROVISIONED' ? status.mac_address : '';
};

const cancel = () => {
  if (saving.value) return;
  dialog.value?.close();
  emit('close');
};

const provision = async () => {
  if (loading.value || saving.value) return;
  const device = devices.value.find(device => device.id === deviceId.value);
  const mac = macAddress.value.trim();
  if (!device || !mac) {
    errorMessage.value = 'Select a device and enter its MAC address.';
    return;
  }
  saving.value = true;
  errorMessage.value = '';
  try {
    const response = await fetch(
      `http://localhost:8000/devices/${encodeURIComponent(device.name)}/provision`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mac_address: mac, home_object_id: props.homeObject.id })
      }
    );
    if (!response.ok) throw new Error(`Unable to provision device (HTTP ${response.status}).`);
    emit('provisioned', {
      ...device,
      device_status: {
        case: 'PROVISIONED',
        mac_address: mac,
        home_object_id: props.homeObject.id
      }
    });
    dialog.value?.close();
    emit('close');
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to provision device.';
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  dialog.value?.showModal();
  void loadDevices();
});
</script>

<template>
  <dialog ref="dialog" class="provision-dialog" aria-labelledby="provision-title" @cancel.prevent="cancel">
    <form @submit.prevent="provision">
      <h2 id="provision-title" class="h5">Connect device to {{ homeObject.name }}</h2>
      <p v-if="loading" role="status">Loading devices...</p>
      <fieldset :disabled="loading || saving">
        <BFormGroup label="Device" label-for="provision-device" class="mb-3">
        <BFormSelect id="provision-device" v-model="deviceId" required autofocus @update:model-value="selectDevice">
          <BFormSelectOption disabled value="">Select a device</BFormSelectOption>
          <BFormSelectOption v-for="device in devices" :key="device.id" :value="device.id">
            {{ device.name }}{{ device.device_status.case === 'PROVISIONED' ? ' (provisioned)' : '' }}
          </BFormSelectOption>
        </BFormSelect>
        </BFormGroup>
        <BFormGroup label="MAC address" label-for="provision-mac" class="mb-3">
          <BFormInput id="provision-mac" v-model="macAddress" required placeholder="AA:BB:CC:DD:EE:FF" />
        </BFormGroup>
        <p v-if="!loading && !devices.length && !errorMessage">
          No devices available. Register a device before connecting it.
        </p>
        <p>Connecting a provisioned device replaces its current home-object connection.</p>
        <BButton type="submit" variant="primary" :disabled="!deviceId || !macAddress.trim()">
          {{ saving ? 'Connecting...' : 'Connect device' }}
        </BButton>
      </fieldset>
      <p v-if="errorMessage" role="alert" class="alert alert-danger">{{ errorMessage }}</p>
      <BButton v-if="errorMessage && !devices.length" type="button" variant="outline-primary" class="me-2" :disabled="loading" @click="loadDevices">
        Retry loading devices
      </BButton>
      <BButton type="button" variant="outline-secondary" :disabled="saving" @click="cancel">Cancel</BButton>
    </form>
  </dialog>
</template>

<style scoped>
.provision-dialog {
  width: min(360px, calc(100vw - 2rem));
  margin: auto;
  padding: 1rem;
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.provision-dialog::backdrop {
  background: rgb(0 0 0 / 40%);
}

fieldset {
  border: 0;
  padding: 0;
  margin: 1rem 0;
  min-width: 0;
}

</style>
