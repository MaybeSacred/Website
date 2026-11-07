<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { BButton } from 'bootstrap-vue-next'
import { useTheme } from './composables/useTheme'

const { theme, toggleTheme } = useTheme()
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <nav>
        <RouterLink to="/pi-website">Home</RouterLink>
        <RouterLink to="/pi-website/about">About</RouterLink>
      </nav>
      <BButton type="button" variant="outline-secondary" size="sm" class="theme-toggle" :aria-pressed="theme === 'dark'" @click="toggleTheme">
        {{ theme === 'dark' ? 'Light mode' : 'Dark mode' }}
      </BButton>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

.theme-toggle {
  display: block;
  margin: 1rem auto 0;
  padding: 0.25rem 0.75rem;
  color: var(--color-text);
  background: var(--color-background-soft);
  border: 1px solid var(--color-border-hover);
  border-radius: 4px;
  white-space: nowrap;
  cursor: pointer;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
