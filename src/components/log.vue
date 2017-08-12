<template>
  <div>
    <el-collapse>
      <el-collapse-item title="设备列表" class="deviceList">
        <a v-for="dev in $store.state.devices" @click="$emit('locate', dev.lat, dev.lon)" style="cursor:pointer;">{{dev.ip}}<br/></a>
      </el-collapse-item>
    </el-collapse>
    <el-col :span="16" :offset="4" class="logInfo">
      <h3 style="margin: 0">扫描日志</h3>
      <span v-for="log in $store.state.logInfo.slice(-5)" :class='log.level'>{{log.message}}<br/></span>
    </el-col>
  </div>
</template>
<style lang="scss">
  .logInfo{
    position: fixed;
    bottom: 0;
    background-color: rgba(150,150,150,0.6);
    padding: 1em;
    height: 10.17em;
  }
  .deviceList{
    position: fixed;
    top: 10%;
    right: 5%;
    border: 0;
    width: 12em;
    .el-collapse-item__content{
      height: 20.6em;
      overflow: auto;
    }
  }
  .INFO{
    color: darkblue;
  }
  .DEBUG{
    color: dimgray;
  }
  .WARNING{
    color: lightpink;
  }
  .ERROR{
    color: darkred;
  }
</style>
