import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ProvisionDeviceDialog from '../ProvisionDeviceDialog.vue'
import type { HomeObject } from '@/types/homeObject'
import type { Device } from '@/types/device'

const homeObject: HomeObject = {
  id: 'home-id', name: 'Living Room', creation_date: '2026-01-01',
  tags: [], user_data: {}, location: { x: 0, y: 0, z: 0 },
  orientation: { x: 0, y: 0, z: 0, w: 1 },
}
const devices: Device[] = [
  {
    id: 'device-id', name: 'Sensor / one', creation_date: '2026-01-01',
    device_status: { case: 'UNPROVISIONED' },
  },
  {
    id: 'other-id', name: 'Other sensor', creation_date: '2026-01-01',
    device_status: { case: 'PROVISIONED', mac_address: 'old-mac', home_object_id: 'old-home' },
  },
]

describe('ProvisionDeviceDialog', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true, json: async () => structuredClone(devices),
    }))
    Object.defineProperty(HTMLDialogElement.prototype, 'showModal', {
      configurable: true,
      value: function (this: HTMLDialogElement) { this.open = true },
    })
    Object.defineProperty(HTMLDialogElement.prototype, 'close', {
      configurable: true,
      value: function (this: HTMLDialogElement) { this.open = false },
    })
  })
  afterEach(() => {
    vi.restoreAllMocks()
    Reflect.deleteProperty(HTMLDialogElement.prototype, 'showModal')
    Reflect.deleteProperty(HTMLDialogElement.prototype, 'close')
    vi.unstubAllGlobals()
  })

  it('loads devices and provisions the selected device with the home object and trimmed MAC', async () => {
    const wrapper = mount(ProvisionDeviceDialog, { props: { homeObject } })
    await flushPromises()
    expect(wrapper.get<HTMLDialogElement>('dialog').element.open).toBe(true)
    expect(wrapper.text()).toContain('Living Room')
    expect(wrapper.get('#provision-device').classes()).toContain('form-select')
    expect(wrapper.get('#provision-mac').classes()).toContain('form-control')
    expect(wrapper.get('button[type="submit"]').classes()).toContain('btn-primary')
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/devices/')
    await wrapper.get('#provision-device').setValue('device-id')
    await wrapper.get('#provision-mac').setValue(' AA:BB:CC:DD:EE:FF ')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(fetch).toHaveBeenLastCalledWith(
      'http://localhost:8000/devices/Sensor%20%2F%20one/provision',
      {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mac_address: 'AA:BB:CC:DD:EE:FF', home_object_id: 'home-id' }),
      },
    )
    expect(wrapper.emitted('provisioned')).toEqual([[{
      ...devices[0],
      device_status: {
        case: 'PROVISIONED', mac_address: 'AA:BB:CC:DD:EE:FF', home_object_id: 'home-id',
      },
    }]])
    expect(wrapper.emitted('close')).toHaveLength(1)
    wrapper.unmount()
  })

  it('prefills existing MAC addresses and clears them when switching to an unprovisioned device', async () => {
    const wrapper = mount(ProvisionDeviceDialog, { props: { homeObject } })
    await flushPromises()
    await wrapper.get('#provision-device').setValue('other-id')
    expect(wrapper.get<HTMLInputElement>('#provision-mac').element.value).toBe('old-mac')
    await wrapper.get('#provision-device').setValue('device-id')
    expect(wrapper.get<HTMLInputElement>('#provision-mac').element.value).toBe('')
    wrapper.unmount()
  })

  it('cancels by button or Escape without making a provisioning request', async () => {
    for (const escape of [false, true]) {
      const wrapper = mount(ProvisionDeviceDialog, { props: { homeObject } })
      await flushPromises()
      await wrapper.get('#provision-device').setValue('device-id')
      await wrapper.get('#provision-mac').setValue('mac')
      if (escape) await wrapper.get('dialog').trigger('cancel')
      else await wrapper.findAll('button').find(button => button.text() === 'Cancel')!.trigger('click')
      expect(wrapper.emitted('close')).toHaveLength(1)
      expect(wrapper.emitted('provisioned')).toBeUndefined()
      expect(wrapper.get<HTMLDialogElement>('dialog').element.open).toBe(false)
      wrapper.unmount()
    }
    expect(fetch).toHaveBeenCalledTimes(2)
  })

  it('rejects missing device and whitespace-only MAC without writing', async () => {
    const wrapper = mount(ProvisionDeviceDialog, { props: { homeObject } })
    await flushPromises()
    await wrapper.get('form').trigger('submit')
    await wrapper.get('#provision-device').setValue('device-id')
    await wrapper.get('#provision-mac').setValue('   ')
    await wrapper.get('form').trigger('submit')
    expect(wrapper.get('[role="alert"]').text()).toContain('Select a device')
    expect(fetch).toHaveBeenCalledTimes(1)
    wrapper.unmount()
  })

  it('displays load errors, supports retry, and reports an empty device list', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response(null, { status: 503 }))
    const wrapper = mount(ProvisionDeviceDialog, { props: { homeObject } })
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('HTTP 503')
    vi.mocked(fetch).mockResolvedValueOnce(new Response('[]', { status: 200 }))
    await wrapper.findAll('button').find(button => button.text() === 'Retry loading devices')!.trigger('click')
    await flushPromises()
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('No devices available')
    wrapper.unmount()
  })

  it('keeps input and the modal open on HTTP or network failure for retry', async () => {
    const wrapper = mount(ProvisionDeviceDialog, { props: { homeObject } })
    await flushPromises()
    await wrapper.get('#provision-device').setValue('device-id')
    await wrapper.get('#provision-mac').setValue('mac')
    vi.mocked(fetch).mockResolvedValueOnce(new Response(null, { status: 422 }))
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('HTTP 422')
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network unavailable'))
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('Network unavailable')
    expect(wrapper.get<HTMLInputElement>('#provision-mac').element.value).toBe('mac')
    expect(wrapper.get<HTMLDialogElement>('dialog').element.open).toBe(true)
    expect(wrapper.emitted('close')).toBeUndefined()
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.emitted('provisioned')).toHaveLength(1)
    wrapper.unmount()
  })

  it('blocks duplicate submits and cancellation during a write', async () => {
    const wrapper = mount(ProvisionDeviceDialog, { props: { homeObject } })
    await flushPromises()
    await wrapper.get('#provision-device').setValue('device-id')
    await wrapper.get('#provision-mac').setValue('mac')
    let complete!: (response: Response) => void
    vi.mocked(fetch).mockReturnValueOnce(new Promise(resolve => { complete = resolve }))
    await wrapper.get('form').trigger('submit')
    await wrapper.get('form').trigger('submit')
    await wrapper.get('dialog').trigger('cancel')
    expect(wrapper.get<HTMLFieldSetElement>('fieldset').element.disabled).toBe(true)
    expect(fetch).toHaveBeenCalledTimes(2)
    expect(wrapper.emitted('close')).toBeUndefined()
    complete(new Response(null, { status: 200 }))
    await flushPromises()
    expect(wrapper.emitted('close')).toHaveLength(1)
    wrapper.unmount()
  })
})
