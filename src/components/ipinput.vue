<template>
  <div class="ip-input-container">
    <div class="ip-segment" v-for="(segment, index) in segments">
      <input type="text" maxlength="3" class="ip-segment-input" :value="segment"
             @keydown="onInputKeydown($event, index)"
             @input="onInput($event, index)"
             @blur="onInputBlur()"
             @paste="onPaste($event, index)">
      <b v-if="index != segments.length - 1">.</b>
    </div>
  </div>
</template>

<script>
  /* global document */
  /**
   * get the cursor position of the element
   * @param  {Element} el the element
   * @return {Integer}    the position fo the cursor
   */
  function getRange (el) {
    let cuRange
    let tbRange
    let headRange
    let range
    let dupRange
    let ret = {}
    if (el.setSelectionRange) {
      // standard
      ret.begin = el.selectionStart
      ret.end = el.selectionEnd
      ret.result = el.value.substring(ret.begin, ret.end)
    } else if (document.selection) {
      // ie
      if (el.tagName.toLowerCase() === 'input') {
        cuRange = document.selection.createRange()
        tbRange = el.createTextRange()
        tbRange.collapse(true)
        tbRange.select()
        headRange = document.selection.createRange()
        headRange.setEndPoint('EndToEnd', cuRange)
        ret.begin = headRange.text.length - cuRange.text.length
        ret.end = headRange.text.length
        ret.result = cuRange.text
        cuRange.select()
      } else if (el.tagName.toLowerCase() === 'textarea') {
        range = document.selection.createRange()
        dupRange = range.duplicate()
        dupRange.moveToElementText(el)
        dupRange.setEndPoint('EndToEnd', range)
        ret.begin = dupRange.text.length - range.text.length
        ret.end = dupRange.text.length
        ret.result = range.text
      }
    }
    el.focus()
    return ret
  }
  export default {
    props: {
      ip: {
        type: String,
        required: true
      },
      onChange: Function,
      onBlur: Function
    },
    data () {
      return {
        segments: ['', '', '', '']
      }
    },
    watch: {
      ip (ip) {
        this.syncIp(ip)
      }
    },
    methods: {
      onInputKeydown (event, index) {
        let keyCode = event.keyCode || event.which
        let value = event.target.value
        if (keyCode === 8 || keyCode === 37) {
          // move the cursor to previous input if backspace and left arrow is pressed at the begin of one input
          if ((value.length === 0 || getRange(event.target).end === 0) &&
            index > 0) {
            this.$el.getElementsByTagName('input')[index - 1].focus()
          }
        } else if (keyCode === 39) {
          if (getRange(event.target).end === value.length &&
            index < 3) {
            // move to cursor to the next input if right arrow is pressed at the end of one input
            this.$el.getElementsByTagName('input')[index + 1].focus()
          }
        }
      },
      onInput (event, index) {
        let value = event.target.value
        event.target.value = this.segments[index]
        if ((value.charAt(value.length - 1) === '.') && index < 3) {
          this.$el.getElementsByTagName('input')[index + 1].focus()
          return
        }
        if (value === '') {
          this.segments.splice(index, 1, '')
          return
        }
        let segment = Number(value)
        if (isNaN(segment)) {
          return
        } else if (segment > 255 || segment < 0) {
          // set the segment to 255 if out of ip range
          this.segments.splice(index, 1, 255)
        } else {
          this.segments.splice(index, 1, segment)
        }
        // jump to next input
        if (value.length === 3 && index < 3) {
          this.$el.getElementsByTagName('input')[index + 1].focus()
        }
      },
      onInputBlur () {
        setTimeout(() => {
          let className = document.activeElement.className
          if (className.indexOf('ip-segment-input') === -1) {
            if (this.onBlur) {
              this.onBlur(this.segments.join('.'))
            }
          }
        }, 50)
      },
      onPaste (e, index) {
        let pasteText = e.clipboardData.getData('text/plain')
        let segments = pasteText.split('.')
        segments.forEach((segment, i) => {
          let value = Number(segment)
          if (index + i < 4 && !isNaN(value) &&
            value >= 0 && value <= 255) {
            this.segments.splice(index + i, 1, value)
          }
        })
        e.preventDefault()
      },
      syncIp (ip) {
        if (ip === '') {
          this.segments = ['', '', '', '']
        }
        if (ip && ip.indexOf('.') !== -1) {
          ip.split('.').map((segment, index) => {
            if (segment === '') {
              this.segments.splice(index, 1, '')
              return ''
            }
            segment = Number(segment)
            if (isNaN(segment) || segment < 0 || segment > 255) {
              segment = 255
            }
            this.segments.splice(index, 1, segment)
            return segment
          })
        }
      }
    },
    mounted () {
      this.syncIp(this.ip)
      this.$watch(() => {
        return this.segments.join('.')
      }, (val, oldValue) => {
        if (val !== oldValue) {
          if (val === '...') {
            val = ''
          }
          if (this.onChange) {
            this.onChange(val)
          }
        }
      })
    }
  }
</script>

<style lang="scss" scoped>
  .ip-input-container {
    display: flex;
    border: 1px solid #ccc;
    width: 100%;
    height: 100%;
    min-width: 11em;
    justify-content: center;
    align-items: center;
  }
  input {
    width: 2em;
    font-size: inherit;
    border: none;
    outline: none;
    text-align: center;
    text-indent: 0;
    margin: 0;
    padding: 0;
  }
  /* try to be the same style as el-input, optional */
  .ip-input-container {
    border-radius: 4px;
  }
</style>
