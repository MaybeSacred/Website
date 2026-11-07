import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import PiPicoConfiguration from '../PiPicoConfiguration.vue'

const configuration = {
  general: {
    measurement_interval: 60, heartbeat_interval: 30, data_write_interval: 120,
    enable_dht20_sensor: true, enable_sht30_sensor: false, enable_sht40_sensor: true,
    enable_stemma_moisture_sensor: false, enable_moisture_temp_humidity: true,
  },
  network: { network_ssid: 'Home', ingestion_server_url: 'server', ingestion_server_port: 8000 },
  logging: { enable_logging: true, log_level: 2 },
  version: '1.0',
}

describe('PiPicoConfiguration', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      json: async () => structuredClone(configuration),
    }))
  })
  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('renders Bootstrap inputs and switches with the current configuration without adding changes', async () => {
    const wrapper = mount(PiPicoConfiguration, { props: { ipAddress: 'pi.local', exists: true } })
    await flushPromises()
    expect(wrapper.classes()).toContain('card')
    expect(wrapper.get('#network-ssid').classes()).toContain('form-control')
    expect(wrapper.get<HTMLInputElement>('#enable-dht20-sensor').element.checked).toBe(true)
    expect(wrapper.get<HTMLInputElement>('#enable-sht30-sensor').element.checked).toBe(false)
    expect(wrapper.get('#enable-dht20-sensor').classes()).toContain('form-check-input')
    expect(wrapper.get('#log-level').attributes('min')).toBe('1')
    expect(wrapper.get('#log-level').attributes('max')).toBe('3')
    await wrapper.get('form').trigger('submit')
    expect(fetch).toHaveBeenLastCalledWith('http://pi.local/configuration', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ general: {}, network: {}, logging: { enable_logging: true } }),
    })
    await flushPromises()
    wrapper.unmount()
  })

  it('sends numeric edits and boolean switches while preserving partial-update payloads', async () => {
    const wrapper = mount(PiPicoConfiguration, { props: { ipAddress: 'pi.local', exists: true } })
    await flushPromises()
    await wrapper.get('#measurement-interval').setValue('15')
    await wrapper.get('#heartbeat-interval').setValue('20')
    await wrapper.get('#ingestion-server-port').setValue('9000')
    await wrapper.get('#network-ssid').setValue('New network')
    await wrapper.get('#enable-dht20-sensor').setValue(false)
    await wrapper.get('#enable-sht30-sensor').setValue(true)
    await wrapper.get('#enable-logging').setValue(false)
    expect(wrapper.find('#log-level').exists()).toBe(false)
    await wrapper.get('form').trigger('submit')
    expect(fetch).toHaveBeenLastCalledWith('http://pi.local/configuration', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        general: {
          measurement_interval: 15, heartbeat_interval: 20,
          enable_dht20_sensor: false, enable_sht30_sensor: true,
        },
        network: { ingestion_server_port: 9000, network_ssid: 'New network' },
        logging: { enable_logging: false },
      }),
    })
    await flushPromises()
    expect(wrapper.get<HTMLInputElement>('#enable-dht20-sensor').element.checked).toBe(true)
    wrapper.unmount()
  })

  it('preserves relay toggling and the unavailable configuration message', async () => {
    const wrapper = mount(PiPicoConfiguration, { props: { ipAddress: 'pi.local', exists: true } })
    await flushPromises()
    for (const on of [true, false]) {
      vi.mocked(fetch).mockResolvedValueOnce(new Response(JSON.stringify({ on })))
      await wrapper.findAll('button').find(button => button.text() === 'Power Cycle')!.trigger('click')
      await flushPromises()
      expect(fetch).toHaveBeenLastCalledWith('http://pi.local/relay', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ on }),
      })
    }
    await wrapper.setProps({ exists: false })
    expect(wrapper.text()).toContain('No configuration found')
    expect(wrapper.find('form').exists()).toBe(false)
    wrapper.unmount()
  })
})
