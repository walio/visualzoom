<template>
  <div id="app">
    <websocket ref="websocket"></websocket>
    <echart-map id="map" @showConfig="$refs.config.open()" @showReport="$refs.report.open()"></echart-map>
    <config ref="config"></config>
    <report ref="report"></report>
  </div>
</template>

<script>
  export default {
    name: 'app',
    data () {
      return {
      }
    },
    mounted () {
    },
    methods: {
    }
  }
</script>

<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
  }
</style>
