import { afterEach, assert, beforeEach, describe, expect, it, vi } from 'vitest'
import { config, flushPromises, shallowMount } from '@vue/test-utils'
import { Circle, Group, Line, Rect, Stage, Text } from 'vue-konva'
import MapView from '../MapView.vue'
import { useTheme } from '@/composables/useTheme'
import ProvisionDeviceDialog from '../ProvisionDeviceDialog.vue'

describe('MapView', () => {
  const previousStubs = config.global.stubs
  const objectClickEvent = (id: string) => ({
    target: { id: () => '', getStage: () => ({}), getParent: () => ({ id: () => id }) },
  })
  const objects = [
    {
      id: 'one', name: 'Living Room', location: { x: 100, y: 120, z: 0 },
      tags: ['indoor', 'sensor'], user_data: { model: 'Temperature sensor', notes: '<b>Plain text</b>' },
    },
    {
      id: 'two', name: 'Kitchen', location: { x: 250, y: 300, z: 0 },
      tags: [], user_data: {},
    },
  ]

  beforeEach(() => {
    config.global.stubs = { ...previousStubs, BButton: false, BFormInput: false }
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async (url: string) => ({
      ok: true,
      json: async () => url.endsWith('/groups/') ? [] : structuredClone(objects),
    })))
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
    config.global.stubs = previousStubs
    vi.restoreAllMocks()
    Reflect.deleteProperty(HTMLDialogElement.prototype, 'showModal')
    Reflect.deleteProperty(HTMLDialogElement.prototype, 'close')
    vi.unstubAllGlobals()
  })

  const previewNode = (x: number, y: number) => ({
    id: () => 'group-preview', x: () => x, y: () => y,
    getStage: () => ({ getPointerPosition: () => null }),
  })
  const startPlacement = async (wrapper: ReturnType<typeof shallowMount>) => {
    await wrapper.findAll('button').find(b => b.text() === 'Create group')!.trigger('click')
    expect(wrapper.get<HTMLDialogElement>('dialog').element.open).toBe(true)
    await wrapper.get('#group-name').setValue('  New room  ')
    await wrapper.get('dialog form').trigger('submit')
    expect(wrapper.get<HTMLDialogElement>('dialog').element.open).toBe(false)
  }

  it('follows the cursor and creates a 100-unit group in map coordinates only when clicked', async () => {
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    const stage = wrapper.findComponent(Stage)
    const stageNode = { x: () => 200, y: () => -100 }
    Object.assign(stageNode, { getStage: () => stageNode })
    stage.vm.$emit('dragend', { target: stageNode })
    await wrapper.get('[aria-label="Zoom in"]').trigger('click')
    await startPlacement(wrapper)
    const config = stage.props('config')!
    assert(config.x !== undefined && config.y !== undefined && config.scaleX !== undefined && config.scaleY !== undefined)
    expect(wrapper.findComponent(Rect).props('config')).toMatchObject({
      id: 'group-preview', width: 100, height: 100, listening: false,
    })
    expect(wrapper.findComponent(Rect).props('config')?.x).toBeCloseTo((500 - config.x) / config.scaleX - 50)
    expect(wrapper.findComponent(Rect).props('config')?.y).toBeCloseTo((400 - config.y) / config.scaleY - 50)
    window.dispatchEvent(new MouseEvent('pointermove', {
      clientX: (-12.5 + 50) * config.scaleX + config.x,
      clientY: (45 + 50) * config.scaleY + config.y,
    }))
    await flushPromises()
    expect(fetch).toHaveBeenCalledTimes(2)
    expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
    expect(wrapper.findComponent(Rect).props('config')?.x).toBeCloseTo(-12.5)
    expect(wrapper.findComponent(Rect).props('config')?.y).toBeCloseTo(45)
    expect(stage.props('config')?.draggable).toBe(false)
    stage.vm.$emit('click', { target: previewNode(0, 0) })
    await flushPromises()
    const [url, request] = vi.mocked(fetch).mock.calls[2]!
    expect(url).toMatch(/^http:\/\/localhost:8000\/groups\/[0-9a-f-]{36}$/)
    expect(request?.method).toBe('POST')
    expect(JSON.parse(request!.body as string)).toEqual({
      name: 'New room',
      points: [
        { x: -12.5, y: expect.closeTo(45), z: 0 }, { x: 87.5, y: expect.closeTo(45), z: 0 },
        { x: 87.5, y: expect.closeTo(145), z: 0 }, { x: -12.5, y: expect.closeTo(145), z: 0 },
      ],
    })
    expect(wrapper.findComponent(Rect).exists()).toBe(false)
    expect(wrapper.text()).not.toContain('Group created.')
    const polygon = wrapper.findAllComponents(Line).find(line => line.props('config')?.closed)
    expect(polygon?.props('config')?.points).toEqual([
      -12.5, expect.closeTo(45), 87.5, expect.closeTo(45),
      87.5, expect.closeTo(145), -12.5, expect.closeTo(145),
    ])
    wrapper.unmount()
  })

  it('keeps the preview on failure, retries by tap, and blocks duplicate saves and cancellation', async () => {
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    await startPlacement(wrapper)
    const stage = wrapper.findComponent(Stage)
    const target = previewNode(495, 395)
    vi.mocked(fetch).mockResolvedValueOnce(new Response(null, { status: 500 }))
    stage.vm.$emit('tap', { target })
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('HTTP 500')
    expect(wrapper.findComponent(Rect).exists()).toBe(true)
    let finish!: (response: Response) => void
    vi.mocked(fetch).mockReturnValueOnce(new Promise(resolve => { finish = resolve }))
    stage.vm.$emit('tap', { target })
    stage.vm.$emit('click', { target })
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await flushPromises()
    expect(fetch).toHaveBeenCalledTimes(4)
    expect(wrapper.findComponent(Rect).props('config')?.listening).toBe(false)
    expect(wrapper.findAll('button').find(b => b.text() === 'Cancel placement')!.attributes('disabled')).toBeDefined()
    expect(vi.mocked(fetch).mock.calls[2]![0]).toBe(vi.mocked(fetch).mock.calls[3]![0])
    finish(new Response(null, { status: 200 }))
    await flushPromises()
    expect(wrapper.findComponent(Rect).exists()).toBe(false)
    wrapper.unmount()
  })

  it('starts under the cursor and uses the map click position for placement', async () => {
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    vi.spyOn(wrapper.get('.map-container').element, 'getBoundingClientRect').mockReturnValue({
      left: 100, top: 50, x: 100, y: 50, width: 1000, height: 800,
      right: 1100, bottom: 850, toJSON: () => ({}),
    })
    window.dispatchEvent(new MouseEvent('pointermove', { clientX: 320, clientY: 270 }))
    await startPlacement(wrapper)
    await flushPromises()
    expect(wrapper.findComponent(Rect).props('config')).toMatchObject({ x: 170, y: 170 })
    window.dispatchEvent(new MouseEvent('pointermove', { clientX: 420, clientY: 370 }))
    await flushPromises()
    expect(wrapper.findComponent(Rect).props('config')).toMatchObject({ x: 270, y: 270 })
    expect(fetch).toHaveBeenCalledTimes(2)
    const target = { getStage: () => ({ getPointerPosition: () => ({ x: 400, y: 300 }) }) }
    wrapper.findComponent(Stage).vm.$emit('tap', { target })
    await flushPromises()
    const payload = JSON.parse(vi.mocked(fetch).mock.calls[2]![1]!.body as string)
    expect(payload.points[0]).toEqual({ x: 350, y: 250, z: 0 })
    wrapper.unmount()
  })

  it('validates a group name and cancels naming or placement without a write', async () => {
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    await wrapper.findAll('button').find(b => b.text() === 'Create group')!.trigger('click')
    await wrapper.get('#group-name').setValue('   ')
    await wrapper.get('dialog form').trigger('submit')
    expect(wrapper.get('dialog [role="alert"]').text()).toContain('group name')
    expect(wrapper.findComponent(Rect).exists()).toBe(false)
    await wrapper.get('dialog button[type="button"]').trigger('click')
    expect(wrapper.get<HTMLDialogElement>('dialog').element.open).toBe(false)
    await startPlacement(wrapper)
    await wrapper.findAll('button').find(b => b.text() === 'Cancel placement')!.trigger('click')
    expect(wrapper.findComponent(Rect).exists()).toBe(false)
    await startPlacement(wrapper)
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await flushPromises()
    expect(wrapper.findComponent(Rect).exists()).toBe(false)
    expect(fetch).toHaveBeenCalledTimes(2)
    wrapper.unmount()
  })

  it('loads persisted groups and surfaces group-load failures', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true, json: async () => structuredClone(objects),
    } as Response).mockResolvedValueOnce({
      ok: true, json: async () => [{
        id: 'room', name: 'Room', creation_date: '2026-11-07',
        points: [{ x: 0, y: 0, z: 0 }, { x: 10, y: 10, z: 0 }],
      }],
    } as Response)
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    expect(wrapper.findAllComponents(Line).some(line =>
      line.props('config')?.closed && line.props('config')?.points.join(',') === '0,0,10,10'
    )).toBe(true)
    wrapper.unmount()
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true, json: async () => structuredClone(objects),
    } as Response).mockRejectedValueOnce(new Error('Groups unavailable'))
    const failed = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    expect(failed.get('[role="alert"]').text()).toBe('Groups unavailable')
    failed.unmount()
  })

  it('opens provisioning for the selected home object, preserves edits on cancel, and relays success', async () => {
      const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
      await flushPromises()
      wrapper.findComponent(Stage).vm.$emit('click', objectClickEvent('one'))
      await flushPromises()
      await wrapper.get('#object-name').setValue('Unsaved edit')
      await wrapper.findAll('button').find(button => button.text() === 'Connect device')!.trigger('click')
      const modal = wrapper.getComponent(ProvisionDeviceDialog)
      expect(modal.props('homeObject').id).toBe('one')
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
      wrapper.findComponent(Stage).vm.$emit('click', objectClickEvent('two'))
      await flushPromises()
      expect(wrapper.get<HTMLInputElement>('#object-name').element.value).toBe('Unsaved edit')
      modal.vm.$emit('close')
      await flushPromises()
      expect(wrapper.findComponent(ProvisionDeviceDialog).exists()).toBe(false)
      expect(wrapper.get<HTMLInputElement>('#object-name').element.value).toBe('Unsaved edit')
      await wrapper.findAll('button').find(button => button.text() === 'Connect device')!.trigger('click')
      const device = {
        id: 'sensor', name: 'Sensor', creation_date: '2026-01-01',
        device_status: { case: 'PROVISIONED', mac_address: 'mac', home_object_id: 'one' },
      }
      wrapper.getComponent(ProvisionDeviceDialog).vm.$emit('provisioned', device)
      wrapper.getComponent(ProvisionDeviceDialog).vm.$emit('close')
      await flushPromises()
      expect(wrapper.emitted('device-provisioned')).toEqual([[device]])
      expect(wrapper.get('[role="status"]').text()).toContain('Sensor connected')
      wrapper.unmount()
  })

    it('selects a group, drags corners and edges, and persists only its updated points', async () => {
      const points = [
        { x: 100, y: 100, z: 1 }, { x: 200, y: 100, z: 2 },
        { x: 200, y: 200, z: 3 }, { x: 100, y: 200, z: 4 },
      ]
      vi.mocked(fetch).mockImplementation(async (url) => ({
        ok: true, json: async () => String(url).endsWith('/groups/')
          ? [{ id: 'test', name: 'Group', points, creation_date: '2026-11-07' }]
          : structuredClone(objects),
      } as Response))
      const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
      await flushPromises()
      const stage = wrapper.findComponent(Stage)
      stage.vm.$emit('click', { target: {
        id: () => 'map-group-test', getStage: () => ({}),
      } })
      await flushPromises()
      expect(wrapper.get('[role="dialog"]').text()).toContain('Group details')
      expect(wrapper.get('[role="dialog"]').text()).toContain('Drag a corner or edge')
      expect(wrapper.find('#object-name').exists()).toBe(false)
      const corner = () => wrapper.findAllComponents(Circle).find(c => c.props('config')?.id === 'group-corner-0')!
      expect(corner().props('config')).toMatchObject({ x: 100, y: 100, draggable: true })
      const node = { id: () => 'group-corner-0', x: () => 100, y: () => 100, getStage: () => ({}) }
      stage.vm.$emit('dragstart', { target: node })
      node.x = () => 80
      node.y = () => 90
      stage.vm.$emit('dragmove', { target: node })
      await flushPromises()
      expect(corner().props('config')).toMatchObject({ x: 80, y: 90 })
      expect(fetch).toHaveBeenCalledTimes(2)
      stage.vm.$emit('dragend', { target: node })
      await flushPromises()
      const afterCorner = [{ x: 80, y: 90, z: 1 }, ...points.slice(1)]
      expect(fetch).toHaveBeenLastCalledWith('http://localhost:8000/groups/test/update', expect.objectContaining({
        body: JSON.stringify({ points: afterCorner }),
      }))
      const edge = { id: () => 'group-edge-3', x: () => 90, y: () => 145, getStage: () => ({}) }
      stage.vm.$emit('dragstart', { target: edge })
      edge.x = () => 110
      edge.y = () => 175
      stage.vm.$emit('dragend', { target: edge })
      await flushPromises()
      expect(fetch).toHaveBeenLastCalledWith('http://localhost:8000/groups/test/update', expect.objectContaining({
        body: JSON.stringify({ points: [
          { x: 100, y: 120, z: 1 }, points[1], points[2], { x: 120, y: 230, z: 4 },
        ] }),
      }))
      expect(wrapper.text()).not.toContain('Group boundaries saved.')
      await wrapper.get('[aria-label="Close group details"]').trigger('click')
      expect(corner()).toBeUndefined()
      wrapper.unmount()
    })

    it('locks group selection while saving and restores boundaries on a failed save', async () => {
      const points = [{ x: 0, y: 0, z: 0 }, { x: 100, y: 0, z: 0 }, { x: 0, y: 100, z: 0 }]
      vi.mocked(fetch).mockImplementation(async (url) => ({
        ok: true, json: async () => String(url).endsWith('/groups/')
          ? [{ id: 'test', name: 'Group', points, creation_date: '2026-11-07' }]
          : structuredClone(objects),
      } as Response))
      const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
      await flushPromises()
      const stage = wrapper.findComponent(Stage)
      stage.vm.$emit('tap', { target: { id: () => 'map-group-test', getStage: () => ({}) } })
      await flushPromises()
      const node = { id: () => 'group-corner-0', x: () => 0, y: () => 0, getStage: () => ({}) }
      stage.vm.$emit('dragstart', { target: node })
      node.x = () => 25
      let finish!: (response: Response) => void
      vi.mocked(fetch).mockReturnValueOnce(new Promise(resolve => { finish = resolve }))
      stage.vm.$emit('dragend', { target: node })
      await flushPromises()
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
      stage.vm.$emit('click', objectClickEvent('one'))
      await flushPromises()
      expect(wrapper.text()).toContain('Saving...')
      expect(wrapper.get('[role="dialog"]').text()).toContain('Group details')
      finish(new Response(null, { status: 500 }))
      await flushPromises()
      expect(wrapper.get('[role="alert"]').text()).toContain('HTTP 500')
      expect(wrapper.findAllComponents(Circle).find(c => c.props('config')?.id === node.id())!.props('config')).toMatchObject({ x: 0, y: 0 })
      stage.vm.$emit('click', objectClickEvent('one'))
      await flushPromises()
      expect(wrapper.find('[role="dialog"]').exists()).toBe(true)
      expect(wrapper.findAllComponents(Circle).some(c => c.props('config')?.id === node.id())).toBe(false)
      wrapper.unmount()
    })
  it('lists contained objects and rejects a self-intersecting corner drop without saving', async () => {
    vi.mocked(fetch).mockImplementation(async (url) => ({
      ok: true, json: async () => String(url).endsWith('/groups/')
        ? [{
          id: 'test', name: 'Group', creation_date: '2026-11-07',
          points: [{ x: 100, y: 100, z: 0 }, { x: 200, y: 100, z: 0 },
            { x: 200, y: 200, z: 0 }, { x: 100, y: 200, z: 0 }],
        }] : structuredClone(objects),
    } as Response))
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    const stage = wrapper.findComponent(Stage)
    stage.vm.$emit('click', { target: { id: () => 'map-group-test', getStage: () => ({}) } })
    await flushPromises()
    const details = wrapper.get('[role="dialog"]')
    expect(details.findAll('li').map(item => item.text())).toEqual(['Living Room'])
    const node = { id: () => 'group-corner-0', x: () => 100, y: () => 100, getStage: () => ({}) }
    stage.vm.$emit('dragstart', { target: node })
    node.x = () => 250
    node.y = () => 150
    stage.vm.$emit('dragend', { target: node })
    await flushPromises()
    expect(fetch).toHaveBeenCalledTimes(2)
    expect(details.get('[role="alert"]').text()).toContain('self-intersect')
    expect(wrapper.findAllComponents(Circle).find(c => c.props('config')?.id === node.id())!.props('config')).toMatchObject({ x: 100, y: 100 })
    expect(details.findAll('li').map(item => item.text())).toEqual(['Living Room'])
    wrapper.unmount()
  })

  it('renders each name above its circle in the same draggable group', async () => {
    const wrapper = shallowMount(MapView, {
      global: { renderStubDefaultSlot: true },
    })
    await flushPromises()

    const groups = wrapper.findAllComponents(Group)
    expect(groups).toHaveLength(objects.length)
    groups.forEach((group, index) => {
      const object = objects[index]!
      expect(group.props('config')).toMatchObject({
        id: object.id,
        x: object.location.x,
        y: object.location.y,
        draggable: true,
      })
      const label = group.findComponent(Text).props('config')
      const circle = group.findComponent(Circle).props('config')
      assert(label)
      assert(circle)
      expect(label).toMatchObject({
        text: object.name,
        align: 'center',
        verticalAlign: 'bottom',
      })
      expect(label.x + label.width / 2).toBe(circle.x)
      expect(label.y + label.height).toBeLessThan(circle.y - circle.radius)
    })

    wrapper.unmount()
  })

  it('selects by click or tap, displays HTML details, and moves the selection box', async () => {
    const wrapper = shallowMount(MapView, {
      global: { renderStubDefaultSlot: true },
    })
    await flushPromises()

    expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
    expect(wrapper.findComponent(Rect).exists()).toBe(false)

    const groups = wrapper.findAllComponents(Group)
    wrapper.findComponent(Stage).vm.$emit('click', objectClickEvent('one'))
    await flushPromises()

    expect(groups[0]!.findComponent(Rect).props('config')).toMatchObject({
      x: -14, y: -14, width: 28, height: 28,
      stroke: 'black', strokeWidth: 1, listening: false,
    })
    const details = wrapper.get('[role="dialog"]')
    expect(details.element.tagName).toBe('ASIDE')
    expect(wrapper.get<HTMLInputElement>('#object-name').element.value).toBe('Living Room')
    expect(wrapper.get<HTMLInputElement>('#object-tag-0').element.value).toBe('indoor')
    expect(wrapper.get<HTMLInputElement>('#object-tag-1').element.value).toBe('sensor')
    expect(wrapper.get<HTMLInputElement>('#object-key-0').element.value).toBe('model')
    expect(wrapper.get<HTMLInputElement>('#object-value-0').element.value).toBe('Temperature sensor')
    expect(wrapper.get<HTMLInputElement>('#object-value-1').element.value).toBe('<b>Plain text</b>')
    expect(details.find('b').exists()).toBe(false)

    wrapper.findComponent(Stage).vm.$emit('tap', objectClickEvent('two'))
    await flushPromises()

    expect(groups[0]!.findComponent(Rect).exists()).toBe(false)
    expect(groups[1]!.findComponent(Rect).exists()).toBe(true)
    expect(wrapper.findAllComponents(Rect)).toHaveLength(1)
    expect(wrapper.get<HTMLInputElement>('#object-name').element.value).toBe('Kitchen')
    expect(details.text()).toContain('No tags.')
    expect(details.text()).toContain('No user data.')
    expect(details.text()).not.toContain('Living Room')

    wrapper.unmount()
  })

  it('saves edited name, tags and key/value rows without changing location or orientation', async () => {
    const wrapper = shallowMount(MapView, {
      global: { renderStubDefaultSlot: true },
    })
    await flushPromises()
    wrapper.findComponent(Stage).vm.$emit('click', objectClickEvent('one'))
    await flushPromises()

    await wrapper.get('#object-name').setValue('Updated room')
    await wrapper.get('#object-tag-0').setValue('outside')
    await wrapper.get('[aria-label="Remove tag 2"]').trigger('click')
    await wrapper.findAll('button').find(button => button.text() === 'Add tag')!.trigger('click')
    await wrapper.get('#object-tag-1').setValue('new tag')
    await wrapper.get('#object-key-0').setValue('type')
    await wrapper.get('#object-value-0').setValue('Updated sensor')
    await wrapper.get('[aria-label="Remove user data 2"]').trigger('click')
    await wrapper.findAll('button').find(button => button.text() === 'Add user data')!.trigger('click')
    await wrapper.get('#object-key-1').setValue('new key')
    await wrapper.get('#object-value-1').setValue('new value')
    expect(wrapper.findComponent(Group).findComponent(Text).props('config')?.text).toBe('Living Room')

    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(fetch).toHaveBeenLastCalledWith('http://localhost:8000/home-objects/one/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'Updated room',
        tags: ['outside', 'new tag'],
        user_data: { type: 'Updated sensor', 'new key': 'new value' },
      }),
    })
    expect(wrapper.findComponent(Group).findComponent(Text).props('config')?.text).toBe('Updated room')
    expect(wrapper.get('[role="status"]').text()).toBe('Saved.')

    wrapper.findComponent(Stage).vm.$emit('click', objectClickEvent('two'))
    await flushPromises()
    wrapper.findComponent(Stage).vm.$emit('click', objectClickEvent('one'))
    await flushPromises()
    expect(wrapper.get<HTMLInputElement>('#object-name').element.value).toBe('Updated room')
    wrapper.unmount()
  })

  it('sends empty collections when all tags and user data are removed', async () => {
    const wrapper = shallowMount(MapView, {
      global: { renderStubDefaultSlot: true },
    })
    await flushPromises()
    wrapper.findComponent(Stage).vm.$emit('click', objectClickEvent('one'))
    await flushPromises()
    for (let index = 0; index < 2; index++) {
      await wrapper.get('[aria-label="Remove tag 1"]').trigger('click')
      await wrapper.get('[aria-label="Remove user data 1"]').trigger('click')
    }
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(fetch).toHaveBeenLastCalledWith(
      'http://localhost:8000/home-objects/one/update',
      expect.objectContaining({
        body: JSON.stringify({ name: 'Living Room', tags: [], user_data: {} }),
      }),
    )
    wrapper.unmount()
  })

  it('rejects duplicate keys and preserves drafts on HTTP or network failure for retry', async () => {
    const wrapper = shallowMount(MapView, {
      global: { renderStubDefaultSlot: true },
    })
    await flushPromises()
    wrapper.findComponent(Stage).vm.$emit('click', objectClickEvent('one'))
    await flushPromises()
    await wrapper.get('#object-key-1').setValue('model')
    await wrapper.get('form').trigger('submit')
    expect(wrapper.get('[role="alert"]').text()).toContain('unique')
    expect(fetch).toHaveBeenCalledTimes(2)

    await wrapper.get('#object-key-1').setValue('notes')
    await wrapper.get('#object-name').setValue('Draft')
    vi.mocked(fetch).mockResolvedValueOnce(new Response(null, { status: 500 }))
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('HTTP 500')
    expect(wrapper.findComponent(Group).findComponent(Text).props('config')?.text).toBe('Living Room')
    expect(wrapper.get<HTMLInputElement>('#object-name').element.value).toBe('Draft')
    expect(wrapper.find('[role="status"]').exists()).toBe(false)

    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network unavailable'))
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('Network unavailable')

    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    expect(wrapper.findComponent(Group).findComponent(Text).props('config')?.text).toBe('Draft')
    wrapper.unmount()
  })

  it('discards unsaved edits when switching objects and prevents duplicate saves', async () => {
    const wrapper = shallowMount(MapView, {
      global: { renderStubDefaultSlot: true },
    })
    await flushPromises()
    const stage = wrapper.findComponent(Stage)
    stage.vm.$emit('click', objectClickEvent('one'))
    await flushPromises()
    await wrapper.get('#object-name').setValue('Unsaved')
    stage.vm.$emit('click', objectClickEvent('two'))
    await flushPromises()
    stage.vm.$emit('click', objectClickEvent('one'))
    await flushPromises()
    expect(wrapper.get<HTMLInputElement>('#object-name').element.value).toBe('Living Room')

    let finishSave!: (response: Response) => void
    vi.mocked(fetch).mockReturnValueOnce(new Promise(resolve => { finishSave = resolve }))
    await wrapper.get('form').trigger('submit')
    expect(wrapper.get<HTMLFieldSetElement>('fieldset').element.disabled).toBe(true)
    await wrapper.get('form').trigger('submit')
    stage.vm.$emit('click', objectClickEvent('two'))
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await flushPromises()
    expect(fetch).toHaveBeenCalledTimes(3)
    expect(wrapper.get<HTMLInputElement>('#object-name').element.value).toBe('Living Room')

    finishSave(new Response(null, { status: 200 }))
    await flushPromises()
    expect(wrapper.get<HTMLFieldSetElement>('fieldset').element.disabled).toBe(false)
    wrapper.unmount()
  })

  it('dismisses selection using close, Escape, or the empty canvas', async () => {
    const wrapper = shallowMount(MapView, {
      global: { renderStubDefaultSlot: true },
    })
    await flushPromises()
    const stage = wrapper.findComponent(Stage)
    const canvas = {}
    const emptyCanvasEvent = { target: { getStage: () => canvas } }
    emptyCanvasEvent.target = Object.assign(canvas, emptyCanvasEvent.target)

    for (const dismiss of [
      () => wrapper.get('button[aria-label="Close object details"]').trigger('click'),
      () => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })),
      () => stage.vm.$emit('click', emptyCanvasEvent),
      () => stage.vm.$emit('tap', emptyCanvasEvent),
    ]) {
      stage.vm.$emit('click', objectClickEvent('one'))
      await flushPromises()
      expect(wrapper.find('[role="dialog"]').exists()).toBe(true)

      stage.vm.$emit('click', objectClickEvent('one'))
      await flushPromises()
      expect(wrapper.find('[role="dialog"]').exists()).toBe(true)

      await dismiss()
      await flushPromises()
      expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
      expect(wrapper.findComponent(Rect).exists()).toBe(false)
    }

    wrapper.unmount()
  })

  it('uses one-quarter sensitivity for trackpad pinch zoom while preserving the cursor position', async () => {
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    const stage = wrapper.findComponent(Stage)
    const pinch = (deltaY: number) => stage.vm.$emit('wheel', {
      evt: { deltaY, ctrlKey: true, preventDefault: vi.fn() },
      target: { getStage: () => ({ getPointerPosition: () => ({ x: 200, y: 100 }) }) },
    })
    pinch(-1)
    await flushPromises()
    const config = stage.props('config')!
    assert(config.x !== undefined && config.y !== undefined && config.scaleX !== undefined)
    expect(config.scaleX).toBeCloseTo(1.1 ** 0.25)
    expect((200 - config.x) / config.scaleX).toBeCloseTo(200)
    expect((100 - config.y) / config.scaleX).toBeCloseTo(100)
    pinch(1)
    await flushPromises()
    expect(stage.props('config')?.scaleX).toBeCloseTo(1)
    wrapper.unmount()
  })

  it('zooms around the cursor with the wheel, clamps, and resets', async () => {
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    const stage = wrapper.findComponent(Stage)
    const preventDefault = vi.fn()
    const wheel = (deltaY: number) => stage.vm.$emit('wheel', {
      evt: { deltaY, preventDefault },
      target: { getStage: () => ({ getPointerPosition: () => ({ x: 200, y: 100 }) }) },
    })

    wheel(-1)
    await flushPromises()
    const config = stage.props('config') as { x: number; y: number; scaleX: number; scaleY: number }
    expect(preventDefault).toHaveBeenCalled()
    expect(config.scaleX).toBeCloseTo(1.1 ** 0.25)
    // Map point under the cursor stays fixed.
    expect((200 - config.x) / config.scaleX).toBeCloseTo(200)
    expect((100 - config.y) / config.scaleY).toBeCloseTo(100)
    expect(wrapper.text()).toContain('102%')

    for (let i = 0; i < 100; i++) wheel(1)
    await flushPromises()
    expect(stage.props('config')?.scaleX).toBe(0.2)
    expect(wrapper.get('[aria-label="Zoom out"]').attributes('disabled')).toBeDefined()

    await wrapper.get('[aria-label="Zoom in"]').trigger('click')
    expect(stage.props('config')?.scaleX).toBeCloseTo(0.22)

    await wrapper.findAll('button').find(b => b.text() === 'Reset view')!.trigger('click')
    expect(stage.props('config')).toMatchObject({ x: 0, y: 0, scaleX: 1, scaleY: 1, draggable: true })
    wrapper.unmount()
  })

  it('pans by dragging the stage without selecting or saving objects', async () => {
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    const stage = wrapper.findComponent(Stage)
    const stageNode = { x: () => 40, y: () => -30, id: () => '' }
    Object.assign(stageNode, { getStage: () => stageNode })

    stage.vm.$emit('dragstart', { target: stageNode })
    stage.vm.$emit('dragend', { target: stageNode })
    await flushPromises()

    expect(stage.props('config')).toMatchObject({ x: 40, y: -30 })
    expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
    expect(fetch).toHaveBeenCalledTimes(2)
    wrapper.unmount()
  })

  it('saves dragged object location in map coordinates', async () => {
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    const stage = wrapper.findComponent(Stage)
    const groupNode = { id: () => 'one', x: () => 321, y: () => 654, getStage: () => ({}) }

    stage.vm.$emit('dragstart', { target: groupNode })
    stage.vm.$emit('dragend', { target: groupNode })
    await flushPromises()

    expect(fetch).toHaveBeenLastCalledWith('http://localhost:8000/home-objects/one/update', expect.objectContaining({
      body: JSON.stringify({ location: { x: 321, y: 654, z: 0 } }),
    }))
    const groups = wrapper.findAllComponents(Group)
    expect(groups[groups.length - 1]!.props('config')).toMatchObject({ x: 321, y: 654 })
    wrapper.unmount()
  })

  it('draws a 100-unit grid covering the visible area with darker 1000-unit lines and an origin label', async () => {
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    type LineConfig = { points: number[]; stroke: string }
    const lines = () => wrapper.findAllComponents(Line).map(l => l.props('config') as LineConfig)
    const verticalXs = () => lines().filter(l => l.points[0] === l.points[2]).map(l => l.points[0])

    // Default 1000x800 stage at 100%: vertical lines 0..1000, horizontal 0..800.
    expect(verticalXs()).toEqual([0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    expect(lines()).toHaveLength(11 + 9)
    const strokeAt = (x: number) => lines().find(l => l.points[0] === x && l.points[2] === x)!.stroke
    expect(strokeAt(0)).toBe(strokeAt(1000))
    expect(strokeAt(100)).not.toBe(strokeAt(1000))

    const texts = wrapper.findAllComponents(Text).map(t => t.props('config')?.text)
    expect(texts).toContain('(0,0)')

    // Panning into negative space adds negative grid lines.
    const stage = wrapper.findComponent(Stage)
    const stageNode = { x: () => 250, y: () => 0, id: () => '' }
    Object.assign(stageNode, { getStage: () => stageNode })
    stage.vm.$emit('dragmove', { target: stageNode })
    await flushPromises()
    expect(verticalXs()[0]).toBe(-300)
    wrapper.unmount()
  })

  it('switches map canvas colours with the theme so labels and selection stay visible', async () => {
    const { theme } = useTheme()
    theme.value = 'light'
    const wrapper = shallowMount(MapView, { global: { renderStubDefaultSlot: true } })
    await flushPromises()
    wrapper.findComponent(Stage).vm.$emit('click', objectClickEvent('one'))
    await flushPromises()
    const label = () => wrapper.findComponent(Group).findComponent(Text).props('config')?.fill
    const selection = () => wrapper.findComponent(Rect).props('config')?.stroke
    const origin = () => wrapper.findAllComponents(Text).find(t => t.props('config')?.text === '(0,0)')!.props('config')?.fill
    const lineStrokes = () => new Set(wrapper.findAllComponents(Line).map(l => l.props('config')?.stroke))

    expect([label(), selection()]).toEqual(['black', 'black'])
    const lightOrigin = origin()
    const lightStrokes = lineStrokes()

    theme.value = 'dark'
    await flushPromises()
    expect(label()).not.toBe('black')
    expect(selection()).not.toBe('black')
    expect(origin()).not.toBe(lightOrigin)
    expect(lineStrokes()).not.toEqual(lightStrokes)

    theme.value = 'light'
    wrapper.unmount()
  })
})
