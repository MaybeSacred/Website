<script setup lang="ts">
import { BButton, BFormInput } from 'bootstrap-vue-next';
import type { HomeObject, HomeObjectCreationUpdateDto, Vector3Dto } from '@/types/homeObject';
import type { GroupCreationDto, MapGroup } from '@/types/group';
import { isSimplePolygon, pointInPolygon } from '@/utils/polygon';
import { Stage as VStage, Layer as VLayer, Circle as VCircle, Group as VGroup, Text as VText, Rect as VRect, Line as VLine } from 'vue-konva';
import type { KonvaEventObject } from 'konva/lib/Node';
import { computed, nextTick, onMounted, onUnmounted, ref, watch, type VNodeRef } from 'vue';
import { useTheme } from '@/composables/useTheme';
import type { Device } from '@/types/device';
import ProvisionDeviceDialog from './ProvisionDeviceDialog.vue';

const emit = defineEmits<{ 'device-provisioned': [device: Device] }>();

const stageSize = {
  width: 1000,
  height: 800
};

const MIN_ZOOM = 0.2;
const MAX_ZOOM = 5;
const ZOOM_STEP = 1.1;

const view = ref({ x: 0, y: 0, scale: 1 });

const stageConfig = computed(() => ({
  ...stageSize,
  draggable: !pendingGroup.value,
  x: view.value.x,
  y: view.value.y,
  scaleX: view.value.scale,
  scaleY: view.value.scale
}));

// Zooms while keeping the given screen point fixed over the same map point.
const zoomAt = (point: { x: number; y: number }, nextScale: number) => {
  const { x, y, scale } = view.value;
  const clamped = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, nextScale));
  const mapX = (point.x - x) / scale;
  const mapY = (point.y - y) / scale;
  view.value = { x: point.x - mapX * clamped, y: point.y - mapY * clamped, scale: clamped };
};

const handleWheel = (event: KonvaEventObject<WheelEvent>) => {
  event.evt.preventDefault();
  const pointer = event.target.getStage()?.getPointerPosition();
  if (!pointer) return;
  const step = ZOOM_STEP ** 0.25;
  const factor = event.evt.deltaY > 0 ? 1 / step : step;
  zoomAt(pointer, view.value.scale * factor);
};

const center = { x: stageSize.width / 2, y: stageSize.height / 2 };
const zoomIn = () => zoomAt(center, view.value.scale * ZOOM_STEP);
const zoomOut = () => zoomAt(center, view.value.scale / ZOOM_STEP);
const resetView = () => {
  view.value = { x: 0, y: 0, scale: 1 };
};

const { theme } = useTheme();

// Konva draws on a canvas, so it can't use the page's CSS variables directly.
const canvasColors = {
  light: { gridMinor: '#181818', gridMajor: '#eee', origin: '#555', label: 'black', selection: 'black', shadowOpacity: 0.35 },
  dark: { gridMinor: '#555', gridMajor: '#333', origin: '#aaa', label: '#eee', selection: 'white', shadowOpacity: 0.9 }
};
const colors = computed(() => canvasColors[theme.value]);

const GRID_SPACING = 100;
const MAJOR_GRID_SPACING = 1000;

// Grid lines covering only the currently visible map area.
const gridLines = computed(() => {
  const { x, y, scale } = view.value;
  // `+ 0` normalizes -0 when the view is at the origin.
  const left = -x / scale + 0;
  const top = -y / scale + 0;
  const right = left + stageSize.width / scale;
  const bottom = top + stageSize.height / scale;
  const lines: { key: string; points: number[]; major: boolean }[] = [];
  for (let gx = Math.floor(left / GRID_SPACING) * GRID_SPACING; gx <= right; gx += GRID_SPACING) {
    lines.push({ key: `x${gx}`, points: [gx, top, gx, bottom], major: gx % MAJOR_GRID_SPACING === 0 });
  }
  for (let gy = Math.floor(top / GRID_SPACING) * GRID_SPACING; gy <= bottom; gy += GRID_SPACING) {
    lines.push({ key: `y${gy}`, points: [left, gy, right, gy], major: gy % MAJOR_GRID_SPACING === 0 });
  }
  return lines;
});

const handleDragmove = (e: KonvaEventObject<DragEvent>) => {
  if (boundaryDrag.value) {
    moveBoundary(e);
    return;
  }
  if (e.target === e.target.getStage()) {
    view.value = { ...view.value, x: e.target.x(), y: e.target.y() };
  }
};

const stageRef = ref<VNodeRef | null>(null);

const dragItemId = ref<string | null>(null);

const homeObjects = ref<HomeObject[]>([]);

const selectedObjectId = ref<string | null>(null);
const selectedObject = computed(() =>
  homeObjects.value.find(object => object.id === selectedObjectId.value)
);

const draft = ref({
  name: '',
  tags: [] as string[],
  userData: [] as { key: string; value: string }[]
});
const saving = ref(false);
const saveError = ref('');
const saveStatus = ref('');
const provisioningObject = ref<HomeObject | null>(null);
const provisioningStatus = ref('');
const deviceProvisioned = (device: Device) => {
  provisioningStatus.value = `Device ${device.name} connected.`;
  emit('device-provisioned', device);
};
const groups = ref<MapGroup[]>([]);
const selectedGroupId = ref<string | null>(null);
const selectedGroup = computed(() => groups.value.find(group => group.id === selectedGroupId.value));
const groupHomeObjects = computed(() => {
  const group = selectedGroup.value;
  return group ? homeObjects.value.filter(object => pointInPolygon(object.location, group.points)) : [];
});
const savingBoundary = ref(false);
const boundaryDrag = ref<{
  group: MapGroup; handleId: string; indices: number[];
  points: Vector3Dto[]; x: number; y: number;
} | null>(null);
const boundaryHandles = computed(() => {
  const points = selectedGroup.value?.points ?? [];
  return points.flatMap((point, index) => {
    const nextIndex = (index + 1) % points.length;
    const next = points[nextIndex]!;
    const x = (point.x + next.x) / 2;
    const y = (point.y + next.y) / 2;
    return [
      { id: `group-corner-${index}`, indices: [index], x: point.x, y: point.y, points: [] },
      { id: `group-edge-${index}`, indices: [index, nextIndex], x, y,
        points: [point.x - x, point.y - y, next.x - x, next.y - y] }
    ];
  });
});

const moveBoundary = (event: KonvaEventObject<DragEvent>) => {
  const drag = boundaryDrag.value;
  if (!drag || event.target.id() !== drag.handleId) return;
  const dx = event.target.x() - drag.x;
  const dy = event.target.y() - drag.y;
  drag.group.points = drag.points.map((point, index) =>
    drag.indices.includes(index) ? { ...point, x: point.x + dx, y: point.y + dy } : { ...point }
  );
};

const saveBoundary = async (event: KonvaEventObject<DragEvent>) => {
  const drag = boundaryDrag.value;
  if (!drag || event.target.id() !== drag.handleId) return;
  moveBoundary(event);
  boundaryDrag.value = null;
  if (!isSimplePolygon(drag.group.points)) {
    drag.group.points = drag.points;
    groupError.value = 'Group boundaries must not self-intersect or overlap.';
    return;
  }
  savingBoundary.value = true;
  try {
    const response = await fetch(`http://localhost:8000/groups/${drag.group.id}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ points: drag.group.points })
    });
    if (!response.ok) throw new Error(`Unable to save group boundaries (HTTP ${response.status}).`);
  } catch (error) {
    drag.group.points = drag.points;
    groupError.value = error instanceof Error ? error.message : 'Unable to save group boundaries.';
  } finally {
    savingBoundary.value = false;
  }
};
const groupDialog = ref<HTMLDialogElement | null>(null);
const groupName = ref('');
const pendingGroup = ref<{ id: string; name: string; x: number; y: number } | null>(null);
const creatingGroup = ref(false);
const groupError = ref('');
const GROUP_SIZE = 100;
const GROUP_PREVIEW_ID = 'group-preview';
const mapContainer = ref<HTMLDivElement | null>(null);
const pointer = ref<{ x: number; y: number } | null>(null);

const updateGroupPosition = () => {
  if (!pendingGroup.value || creatingGroup.value || !pointer.value || !mapContainer.value) return;
  const bounds = mapContainer.value.getBoundingClientRect();
  pendingGroup.value.x = (pointer.value.x - bounds.left - view.value.x) / view.value.scale - GROUP_SIZE / 2;
  pendingGroup.value.y = (pointer.value.y - bounds.top - view.value.y) / view.value.scale - GROUP_SIZE / 2;
};

const handlePointermove = (event: PointerEvent) => {
  pointer.value = { x: event.clientX, y: event.clientY };
  updateGroupPosition();
};

watch(view, updateGroupPosition);

const openGroupDialog = () => {
  clearSelection();
  groupName.value = '';
  groupError.value = '';
  groupDialog.value?.showModal();
};

const startGroupPlacement = async () => {
  const name = groupName.value.trim();
  if (!name) {
    groupError.value = 'Enter a group name.';
    return;
  }
  pendingGroup.value = {
    id: crypto.randomUUID(),
    name,
    x: (center.x - view.value.x) / view.value.scale - GROUP_SIZE / 2,
    y: (center.y - view.value.y) / view.value.scale - GROUP_SIZE / 2
  };
  groupError.value = '';
  groupDialog.value?.close();
  await nextTick();
  updateGroupPosition();
};

const cancelGroupPlacement = () => {
  if (creatingGroup.value) return;
  pendingGroup.value = null;
  groupError.value = '';
};

const getGroups = async () => {
  try {
    const response = await fetch('http://localhost:8000/groups/');
    if (!response.ok) throw new Error(`Unable to load groups (HTTP ${response.status}).`);
    groups.value = await response.json();
  } catch (error) {
    groupError.value = error instanceof Error ? error.message : 'Unable to load groups.';
  }
};

const placeGroup = async () => {
  const preview = pendingGroup.value;
  if (!preview || creatingGroup.value) return;
  const { x, y } = preview;
  const payload: GroupCreationDto = {
    name: preview.name,
    points: [
      { x, y, z: 0 },
      { x: x + GROUP_SIZE, y, z: 0 },
      { x: x + GROUP_SIZE, y: y + GROUP_SIZE, z: 0 },
      { x, y: y + GROUP_SIZE, z: 0 }
    ]
  };
  creatingGroup.value = true;
  groupError.value = '';
  try {
    if (!isSimplePolygon(payload.points)) throw new Error('Group boundaries must not self-intersect or overlap.');
    const response = await fetch(`http://localhost:8000/groups/${preview.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`Unable to create group (HTTP ${response.status}).`);
    groups.value.push({ ...payload, id: preview.id, creation_date: new Date().toISOString() });
    pendingGroup.value = null;
  } catch (error) {
    groupError.value = error instanceof Error ? error.message : 'Unable to create group.';
  } finally {
    creatingGroup.value = false;
  }
};

watch(selectedObjectId, () => {
  const object = selectedObject.value;
  draft.value = {
    name: object?.name ?? '',
    tags: [...(object?.tags ?? [])],
    userData: Object.entries(object?.user_data ?? {}).map(([key, value]) => ({ key, value }))
  };
  saveError.value = '';
  saveStatus.value = '';
  provisioningStatus.value = '';
});

const clearSelection = () => {
  if (saving.value || provisioningObject.value || savingBoundary.value || boundaryDrag.value) return;
  selectedObjectId.value = null;
  selectedGroupId.value = null;
};

const handleStageClick = (event: KonvaEventObject<MouseEvent | TouchEvent>) => {
  if (pendingGroup.value) {
    if (!creatingGroup.value) {
      const position = event.target.getStage()?.getPointerPosition();
      if (position) {
        pendingGroup.value.x = (position.x - view.value.x) / view.value.scale - GROUP_SIZE / 2;
        pendingGroup.value.y = (position.y - view.value.y) / view.value.scale - GROUP_SIZE / 2;
      }
      void placeGroup();
    }
    return;
  }
  if (saving.value || provisioningObject.value || savingBoundary.value || boundaryDrag.value) return;
  if (event.target === event.target.getStage()) {
    clearSelection();
  } else {
    const group = groups.value.find(group => `map-group-${group.id}` === event.target.id());
    if (group) {
      selectedObjectId.value = null;
      selectedGroupId.value = group.id;
      groupError.value = '';
      return;
    }
    const objectId = event.target.getParent()?.id();
    if (homeObjects.value.some(object => object.id === objectId)) {
      selectedGroupId.value = null;
      selectedObjectId.value = objectId ?? null;
    }
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  if (provisioningObject.value) return;
  if (event.key === 'Escape') {
    cancelGroupPlacement();
    clearSelection();
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
  window.addEventListener('pointermove', handlePointermove);
});
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
  window.removeEventListener('pointermove', handlePointermove);
});

const getHomeObjects = async () => {
  const response = await fetch(`http://localhost:8000/home-objects/`, {
    method: 'GET',
  });
  const json: HomeObject[] = await response.json();
  homeObjects.value = json;
}

const updateHomeObject = async (id: string, update: Partial<HomeObjectCreationUpdateDto>) => {
  const response = await fetch(`http://localhost:8000/home-objects/${id}/update`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(update)
  });
  if (!response.ok) {
    throw new Error(`Unable to update home object (HTTP ${response.status}).`);
  }
}

const saveObject = async () => {
  const object = selectedObject.value;
  if (!object || saving.value) return;
  saveError.value = '';
  saveStatus.value = '';
  const keys = draft.value.userData.map(entry => entry.key);
  if (new Set(keys).size !== keys.length) {
    saveError.value = 'User data keys must be unique.';
    return;
  }
  const update = {
    name: draft.value.name,
    tags: [...draft.value.tags],
    user_data: Object.fromEntries(draft.value.userData.map(({ key, value }) => [key, value]))
  };
  saving.value = true;
  try {
    await updateHomeObject(object.id, update);
    Object.assign(object, update);
    saveStatus.value = 'Saved.';
  } catch (error) {
    saveError.value = error instanceof Error ? error.message : 'Unable to save home object.';
  } finally {
    saving.value = false;
  }
};

const createHomeObjects = async () => {
  const response = await fetch(`http://localhost:8000/home-objects/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'New Home Object',
      tags: [],
      user_data: {},
      location: { x: 0, y: 0, z: 0 },
      orientation: { x: 0, y: 0, z: 0, w: 1 }
    } satisfies HomeObjectCreationUpdateDto)
  });
  // const json: HomeObject[] = await response.json();
  // devices.value = json;

}

const handleDragstart = (e: KonvaEventObject<DragEvent>) => {
  if (provisioningObject.value) return;
  if (e.target === e.target.getStage()) return;
  const handle = boundaryHandles.value.find(handle => handle.id === e.target.id());
  if (handle && selectedGroup.value && !savingBoundary.value) {
    boundaryDrag.value = {
      group: selectedGroup.value, handleId: handle.id, indices: handle.indices,
      points: selectedGroup.value.points.map(point => ({ ...point })),
      x: e.target.x(), y: e.target.y()
    };
    groupError.value = '';
    return;
  }
  selectedGroupId.value = null;
  // save drag element:
  dragItemId.value = e.target.id();
  selectedObjectId.value = dragItemId.value;
  console.log('Dragging started for item:', dragItemId.value, e);
  // move current element to the top:
  const item = homeObjects.value.find(i => i.id === dragItemId.value);
  if (!item) return;
  const index = homeObjects.value.indexOf(item);
  homeObjects.value.splice(index, 1);
  homeObjects.value.push(item);
};

const handleDragend = async (e: KonvaEventObject<DragEvent>) => {
  if (boundaryDrag.value) {
    await saveBoundary(e);
    return;
  }
  if (e.target === e.target.getStage()) {
    view.value = { ...view.value, x: e.target.x(), y: e.target.y() };
    return;
  }
  if (dragItemId.value) {
    console.log('Dragging ended for item with id:', dragItemId.value);
    const item = homeObjects.value.find(i => i.id === dragItemId.value);
    if (!item) return;
    // The group's position is already in map coordinates, independent of pan/zoom.
    const location = { x: e.target.x(), y: e.target.y(), z: item.location.z ?? 0 };
    item.location = location;
    try {
      await updateHomeObject(dragItemId.value, { location });
    } catch (error) {
      saveError.value = error instanceof Error ? error.message : 'Unable to save object location.';
    }
  }
  dragItemId.value = null;
};

getHomeObjects();
getGroups();
</script>

<template>
  <div class="map-toolbar">
    <BButton type="button" variant="primary" :disabled="saving || savingBoundary || !!boundaryDrag || !!pendingGroup" @click="openGroupDialog">Create group</BButton>
    <BButton type="button" variant="outline-primary" @click="createHomeObjects">Add Home Object</BButton>
    <BButton type="button" variant="outline-secondary" aria-label="Zoom out" :disabled="view.scale <= MIN_ZOOM" @click="zoomOut">−</BButton>
    <span aria-live="polite">{{ Math.round(view.scale * 100) }}%</span>
    <BButton type="button" variant="outline-secondary" aria-label="Zoom in" :disabled="view.scale >= MAX_ZOOM" @click="zoomIn">+</BButton>
    <BButton type="button" variant="outline-secondary" @click="resetView">Reset view</BButton>
  </div>
  <p v-if="pendingGroup" role="status">
    Move the cursor to position {{ pendingGroup.name }}, then click the map to create the group.
    <BButton type="button" variant="outline-secondary" size="sm" :disabled="creatingGroup" @click="cancelGroupPlacement">Cancel placement</BButton>
    <span v-if="creatingGroup">Creating...</span>
  </p>
  <div ref="mapContainer" class="map-container">
    <div class="map-notifications">
      <p v-if="groupError && !groupDialog?.open && !selectedGroup" role="alert">{{ groupError }}</p>
    </div>
    <v-stage ref="stageRef" :config="stageConfig" @dragstart="handleDragstart" @dragmove="handleDragmove" @dragend="handleDragend"
      @click="handleStageClick" @tap="handleStageClick" @wheel="handleWheel">
      <v-layer :config="{ listening: false }">
        <v-line v-for="line in gridLines" :key="line.key" :config="{
          points: line.points,
          stroke: line.major ? colors.gridMajor : colors.gridMinor,
          strokeWidth: line.major ? 1 : 0.5,
          strokeScaleEnabled: false
        }" />
        <v-circle :config="{ x: 0, y: 0, radius: 3 / view.scale, fill: colors.origin }" />
        <v-text :config="{
          text: '(0,0)',
          x: 4 / view.scale,
          y: 4 / view.scale,
          fontSize: 12 / view.scale,
          fill: colors.origin
        }" />
      </v-layer>
      <v-layer :config="{ listening: !pendingGroup && !savingBoundary }">
        <v-line v-for="group in groups" :key="group.id" :config="{
          id: `map-group-${group.id}`,
          points: group.points.flatMap(point => [point.x, point.y]),
          closed: true,
          stroke: colors.selection,
          strokeWidth: 1,
          strokeScaleEnabled: false,
          fill: 'rgba(0, 160, 100, 0.2)'
        }" />
      </v-layer>
      <v-layer :config="{ listening: !pendingGroup && !savingBoundary }">
        <template v-for="handle in boundaryHandles" :key="handle.id">
          <v-line v-if="handle.indices.length === 2" :config="{
            id: handle.id, x: handle.x, y: handle.y, points: handle.points,
            stroke: '#00a064', strokeWidth: 2, strokeScaleEnabled: false,
            hitStrokeWidth: 12 / view.scale, draggable: true
          }" />
        </template>
        <template v-for="handle in boundaryHandles" :key="handle.id">
          <v-circle v-if="handle.indices.length === 1" :config="{
            id: handle.id, x: handle.x, y: handle.y, radius: 5 / view.scale,
            fill: '#00a064', stroke: colors.selection, strokeWidth: 1,
            strokeScaleEnabled: false, draggable: true
          }" />
        </template>
      </v-layer>
      <v-layer ref="layer">
        <v-group v-for="device in homeObjects" :key="device.id" :config="{
          id: device.id,
          x: device.location.x,
          y: device.location.y,
          scaleX: dragItemId === device.id ? 1.2 : 1,
          scaleY: dragItemId === device.id ? 1.2 : 1,
          draggable: !saving && !pendingGroup && !savingBoundary && !boundaryDrag,
        }">
          <v-rect v-if="selectedObjectId === device.id" :config="{
            x: -14,
            y: -14,
            width: 28,
            height: 28,
            stroke: colors.selection,
            strokeWidth: 1,
            strokeScaleEnabled: false,
            listening: false
          }" />
          <v-text :config="{
            text: device.name,
            x: -100,
            y: -64,
            width: 200,
            height: 48,
            align: 'center',
            verticalAlign: 'bottom',
            fontSize: 14,
            fill: colors.label
          }" />
          <v-circle :config="{
            x: 0,
            y: 0,
            radius: 10,
            fill: 'blue',
            stroke: 'black',
            strokeWidth: 2,
            opacity: 0.8,
            shadowColor: 'black',
            shadowBlur: dragItemId === device.id ? 12 : 4,
            shadowOffsetX: dragItemId === device.id ? 4 : 1,
            shadowOffsetY: dragItemId === device.id ? 6 : 2,
            shadowOpacity: colors.shadowOpacity,
            shadowForStrokeEnabled: false
          }" />
        </v-group>
      </v-layer>
      <v-layer>
        <v-rect v-if="pendingGroup" :config="{
          id: GROUP_PREVIEW_ID,
          x: pendingGroup.x,
          y: pendingGroup.y,
          width: GROUP_SIZE,
          height: GROUP_SIZE,
          fill: 'rgba(0, 160, 100, 0.5)',
          stroke: colors.selection,
          strokeWidth: 1,
          strokeScaleEnabled: false,
          listening: false
        }" />
      </v-layer>
    </v-stage>
    <aside v-if="selectedObject || selectedGroup" class="object-details" role="dialog" aria-labelledby="object-details-title">
      <header class="object-details-header">
        <h2 id="object-details-title">{{ selectedGroup ? 'Group details' : 'Home object details' }}</h2>
        <BButton type="button" variant="outline-secondary" size="sm" :aria-label="selectedGroup ? 'Close group details' : 'Close object details'"
          :disabled="saving || savingBoundary || !!boundaryDrag" @click="clearSelection">Close</BButton>
      </header>
      <template v-if="selectedGroup">
        <h3>Name</h3>
        <p>{{ selectedGroup.name }}</p>
        <p>Drag a corner or edge to change its boundaries.</p>
        <h3>Home objects</h3>
        <ul v-if="groupHomeObjects.length">
          <li v-for="object in groupHomeObjects" :key="object.id">{{ object.name }}</li>
        </ul>
        <p v-else>No home objects in this group.</p>
        <p v-if="savingBoundary" role="status">Saving...</p>
        <p v-if="groupError" role="alert">{{ groupError }}</p>
      </template>
      <template v-else-if="selectedObject">
      <BButton type="button" variant="outline-primary" class="mt-3" :disabled="saving" @click="provisioningStatus = ''; provisioningObject = selectedObject">
        Connect device
      </BButton>
      <p v-if="provisioningStatus" role="status" class="alert alert-success mt-3">{{ provisioningStatus }}</p>
      <form @submit.prevent="saveObject">
        <fieldset :disabled="saving">
          <label for="object-name" class="form-label">Name</label>
          <BFormInput id="object-name" v-model="draft.name" required />
          <h3>Tags</h3>
          <div v-for="(_, index) in draft.tags" :key="index" class="editor-row">
            <label :for="`object-tag-${index}`" class="form-label">Tag {{ index + 1 }}</label>
            <BFormInput :id="`object-tag-${index}`" v-model="draft.tags[index]" required />
            <BButton type="button" variant="outline-danger" size="sm" class="mt-2" :aria-label="`Remove tag ${index + 1}`" @click="draft.tags.splice(index, 1)">Remove</BButton>
          </div>
          <p v-if="!draft.tags.length">No tags.</p>
          <BButton type="button" variant="outline-primary" size="sm" @click="draft.tags.push('')">Add tag</BButton>
          <h3>User data</h3>
          <div v-for="(entry, index) in draft.userData" :key="index" class="editor-row">
            <label :for="`object-key-${index}`" class="form-label">Key {{ index + 1 }}</label>
            <BFormInput :id="`object-key-${index}`" v-model="entry.key" required />
            <label :for="`object-value-${index}`" class="form-label mt-2">Value {{ index + 1 }}</label>
            <BFormInput :id="`object-value-${index}`" v-model="entry.value" />
            <BButton type="button" variant="outline-danger" size="sm" class="mt-2" :aria-label="`Remove user data ${index + 1}`" @click="draft.userData.splice(index, 1)">Remove</BButton>
          </div>
          <p v-if="!draft.userData.length">No user data.</p>
          <BButton type="button" variant="outline-primary" size="sm" @click="draft.userData.push({ key: '', value: '' })">Add user data</BButton>
          <BButton type="submit" variant="primary" class="save-button">{{ saving ? 'Saving...' : 'Save' }}</BButton>
        </fieldset>
        <p v-if="saveError" role="alert" class="alert alert-danger mt-3">{{ saveError }}</p>
        <p v-if="saveStatus" role="status" class="alert alert-success mt-3">{{ saveStatus }}</p>
      </form>
      </template>
    </aside>
    <ProvisionDeviceDialog v-if="provisioningObject" :home-object="provisioningObject"
      @close="provisioningObject = null" @provisioned="deviceProvisioned" />
    <dialog ref="groupDialog" class="group-dialog" aria-labelledby="group-dialog-title">
      <form @submit.prevent="startGroupPlacement">
        <h2 id="group-dialog-title">Name the group</h2>
        <label for="group-name" class="form-label">Group name</label>
        <BFormInput id="group-name" v-model="groupName" required autofocus />
        <p v-if="groupError" role="alert" class="alert alert-danger">{{ groupError }}</p>
        <BButton type="submit" variant="primary" class="me-2">Confirm</BButton>
        <BButton type="button" variant="outline-secondary" @click="groupDialog?.close()">Cancel</BButton>
      </form>
    </dialog>
  </div>
</template>

<style scoped>
.group-dialog {
  width: min(320px, calc(100vw - 2rem));
  margin: auto;
  padding: 1rem;
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.group-dialog::backdrop {
  background: rgb(0 0 0 / 40%);
}

.group-dialog input {
  margin-bottom: 1rem;
}

.map-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.map-container {
  position: relative;
  width: fit-content;
  max-width: 100%;
}

.map-notifications {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  max-width: calc(100% - 2rem);
  z-index: 10;
  background: var(--color-background);
  color: var(--color-text);
}

.object-details {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
  width: min(320px, calc(100% - 2rem));
  max-height: calc(100% - 2rem);
  overflow-y: auto;
  overflow-wrap: anywhere;
  box-sizing: border-box;
  padding: 1rem;
  background: var(--color-background, white);
  color: var(--color-text, black);
  border: 1px solid var(--color-border, black);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgb(0 0 0 / 20%);
}

.object-details-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

h2 {
  margin: 0;
  font-size: 1.1rem;
}

h3 {
  margin-top: 1rem;
}

fieldset {
  border: 0;
  padding: 0;
  margin: 1rem 0 0;
  min-width: 0;
}

label,
input {
  display: block;
}

input {
  width: 100%;
  box-sizing: border-box;
}

.editor-row {
  margin-bottom: 0.75rem;
}

.save-button {
  display: block;
  margin-top: 1rem;
}
</style>
