<template>
  <div id="app">
    <echart-map id="map"></echart-map>
    <control-panel @showConfig="$refs.config.open()" @showReport="$refs.report.open()" @restore="$refs.websocket.emit('restore')" @reconnect="$refs.websocket.emit('reconnect')"></control-panel>
    <config ref="config"></config>
    <report ref="report"></report>
    <websocket ref="websocket"></websocket>
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
    height: 100%;
  }
  #map {
    height: 85%;
    margin-bottom: 2%;
  }
  .chart{
    height: 100%;
  }
</style>
