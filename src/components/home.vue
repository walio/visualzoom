<template>
  <div id="app">
    <websocket ref="websocket"></websocket>
    <echart-map id="map" ref="map" @showConfig="$refs.config.open()" @showReport="$refs.report.open()"></echart-map>
    <config ref="config"></config>
    <report ref="report"></report>
    <log @locate="locate"></log>
  </div>
</template>

<script>
  export default {
    name: 'app',
    data () {
      return {
      }
    },
    beforeCreate () {
      if (window.localStorage.remoteIp) {
        this.$store.state.host = `http://${window.localStorage.remoteIp}`
        this.$store.state.wshost = `ws://${window.localStorage.remoteIp}/ws`
      }
    },
    methods: {
      locate (lat, lon) {
        this.$refs.map.locate(lat, lon)
      }
    }
  }
</script>
