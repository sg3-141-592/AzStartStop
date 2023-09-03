<template>
  <ErrorBoundary>
    <VMList></VMList>
  </ErrorBoundary>
</template>

<script>
import VMList from '../components/VMList.vue'
import ErrorBoundary from '../components/ErrorBoundary.vue'

export default {
  name: 'App',
  components: {
    VMList,
    ErrorBoundary
  }
}
</script>

<style>
</style>
