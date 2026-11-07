import { expect, test } from '@playwright/test'

test('connects a device from home object details and supports cancel, Escape, and retry', async ({ page }) => {
  const writes: unknown[] = []
  let failWrite = true
  await page.route('**/measurement', route => route.fulfill({ json: {} }))
  await page.route('**/data-ingestion/**', route => route.fulfill({ json: [] }))
  await page.route('http://localhost:8000/**', async route => {
    const path = new URL(route.request().url()).pathname
    if (path === '/home-objects/') {
      await route.fulfill({ json: [{
        id: 'home-id', name: 'Living Room', creation_date: '2026-01-01',
        tags: [], user_data: {}, location: { x: 100, y: 120, z: 0 },
        orientation: { x: 0, y: 0, z: 0, w: 1 },
      }] })
    } else if (path === '/devices/') {
      await route.fulfill({ json: [{
        id: 'sensor-id', name: 'Sensor one', creation_date: '2026-01-01',
        device_status: { case: 'UNPROVISIONED' },
      }] })
    } else if (path === '/devices/Sensor%20one/provision') {
      writes.push(route.request().postDataJSON())
      await route.fulfill({ status: failWrite ? 422 : 200, json: null })
    } else {
      await route.fulfill({ json: [] })
    }
  })
  await page.goto('/pi-website/')
  const themeToggle = page.getByRole('button', { name: /^(Dark|Light) mode$/ })
  await themeToggle.click()
  await expect(page.locator('html')).toHaveAttribute(
    'data-bs-theme', (await themeToggle.textContent())?.trim() === 'Light mode' ? 'dark' : 'light',
  )
  const canvas = page.locator('.konvajs-content')
  await expect(canvas).toBeVisible()
  const details = page.locator('aside.object-details')
  await expect(async () => {
    await canvas.click({ position: { x: 100, y: 120 } })
    await expect(details).toBeVisible()
  }).toPass()
  await details.getByLabel('Name', { exact: true }).fill('Unsaved edit')
  await details.getByRole('button', { name: 'Connect device' }).click()
  const modal = page.locator('dialog.provision-dialog')
  await expect(modal).toBeVisible()
  await expect(modal.getByLabel('MAC address')).toHaveClass(/form-control/)
  await expect(modal.getByRole('button', { name: 'Connect device' })).toHaveClass(/btn-primary/)
  await modal.getByLabel('Device', { exact: true }).selectOption('sensor-id')
  await modal.getByLabel('MAC address').fill('AA:BB:CC:DD:EE:FF')
  await modal.getByRole('button', { name: 'Cancel', exact: true }).click()
  await expect(modal).toHaveCount(0)
  expect(writes).toEqual([])
  await expect(details.getByLabel('Name', { exact: true })).toHaveValue('Unsaved edit')
  await details.getByRole('button', { name: 'Connect device' }).click()
  await expect(modal).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(modal).toHaveCount(0)
  await expect(details).toBeVisible()
  expect(writes).toEqual([])
  await details.getByRole('button', { name: 'Connect device' }).click()
  await modal.getByLabel('Device', { exact: true }).selectOption('sensor-id')
  await modal.getByLabel('MAC address').fill(' AA:BB:CC:DD:EE:FF ')
  await modal.getByRole('button', { name: 'Connect device' }).click()
  await expect(modal.getByRole('alert')).toContainText('HTTP 422')
  await expect(modal.getByLabel('MAC address')).toHaveValue(' AA:BB:CC:DD:EE:FF ')
  failWrite = false
  await modal.getByRole('button', { name: 'Connect device' }).click()
  await expect(modal).toHaveCount(0)
  await expect(details.getByRole('status')).toContainText('Sensor one connected')
  await expect(page.locator('li')).toContainText('Sensor one - AA:BB:CC:DD:EE:FF')
  expect(writes).toEqual([
    { mac_address: 'AA:BB:CC:DD:EE:FF', home_object_id: 'home-id' },
    { mac_address: 'AA:BB:CC:DD:EE:FF', home_object_id: 'home-id' },
  ])
})
