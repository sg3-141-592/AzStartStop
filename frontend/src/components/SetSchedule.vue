<template>
  <div v-if="vmData">
    <h1 class="title">{{ vmData.name }}</h1>

    <hr />

    <progress
      v-if="formDisabled"
      class="progress is-small is-primary"
      max="100"
    >
      15%
    </progress>

    <div class="columns is-mobile">
      <div class="column">
        <label class="label">Start Time</label>
        <div class="field has-addons has-addons-right">
          <div class="control is-expanded">
            <input
              v-model="vmData.startTime"
              class="input"
              type="time"
              :disabled="vmData.stopTime == null || formDisabled"
            />
          </div>
          <p v-if="vmData.startTime" class="control">
            <button
              @click="clearStartTime()"
              class="button is-primary"
              :disabled="formDisabled"
            >
              Clear
            </button>
          </p>
        </div>
      </div>
      <div class="column">
        <div class="field">
          <label class="label">Stop Time</label>
          <div class="control">
            <input
              v-model="vmData.stopTime"
              class="input"
              type="time"
              :disabled="formDisabled"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="field">
      <label class="label">Days of Week</label>
      <div class="columns has-text-centered is-mobile">
        <div class="column">
          <input
            type="checkbox"
            v-model="vmData.daysOfWeek.Mon"
            :disabled="formDisabled"
          />
          Mon
        </div>
        <div class="column">
          <input
            type="checkbox"
            v-model="vmData.daysOfWeek.Tue"
            :disabled="formDisabled"
          />
          Tue
        </div>
        <div class="column">
          <input
            type="checkbox"
            v-model="vmData.daysOfWeek.Wed"
            :disabled="formDisabled"
          />
          Wed
        </div>
        <div class="column">
          <input
            type="checkbox"
            v-model="vmData.daysOfWeek.Thu"
            :disabled="formDisabled"
          />
          Thu
        </div>
        <div class="column">
          <input
            type="checkbox"
            v-model="vmData.daysOfWeek.Fri"
            :disabled="formDisabled"
          />
          Fri
        </div>
        <div class="column">
          <input
            type="checkbox"
            v-model="vmData.daysOfWeek.Sat"
            :disabled="formDisabled"
          />
          Sat
        </div>
        <div class="column">
          <input
            type="checkbox"
            v-model="vmData.daysOfWeek.Sun"
            :disabled="formDisabled"
          />
          Sun
        </div>
      </div>
    </div>

    <div v-if="formErrors.length > 0" class="notification is-warning is-light">
      <p v-for="error in formErrors" :key="error">{{ error }}</p>
    </div>

    <div class="field is-grouped is-grouped-right">
      <div class="control">
        <button
          v-if="emptySchedule == false"
          @click="removeSchedule()"
          class="button is-primary"
          :disabled="formDisabled"
        >
          <i class="fa-solid fa-xmark"></i>&nbsp;Remove Schedule
        </button>
      </div>
      <div class="control">
        <button
          @click="updateSchedule()"
          class="button is-link is-right"
          :disabled="formDisabled || formErrors.length > 0"
        >
          <i class="fa-regular fa-clock"></i>&nbsp;Apply
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { timeToDate } from "../helper.js";

export default {
  props: ["vm"],
  emits: ["applied"],
  watch: {
    vm: function (newVal) {
      this.vmData = newVal;
    },
    vmData: {
      handler: function (newVal) {
        let errors = [];
        if (newVal.stopTime == null) {
          errors.push("Schedule requires a stop time");
        } else {
          // Check if at least one day is defined
          let dayCount = 0;
          Object.keys(newVal.daysOfWeek).forEach(function (value) {
            if (newVal.daysOfWeek[value]) {
              dayCount += 1;
            }
          });
          if (dayCount == 0) {
            errors.push("Schedule requires at least 1 day set");
          }
          // Check if start date is before end date
          if (newVal.startTime && newVal.stopTime) {
            if (timeToDate(newVal.startTime) >= timeToDate(newVal.stopTime)) {
              errors.push("Start time should be before stop time");
            }
          }
        }
        this.formErrors = errors;
      },
      deep: true,
    },
  },
  mounted() {
    // Make a deep copy of this
    this.vmData = JSON.parse(JSON.stringify(this.vm));
    // Work out if it's an empty schedule
    if (!this.vm.stopTime) {
      this.emptySchedule = true;
    } else {
      this.emptySchedule = false;
    }
  },
  methods: {
    clearStartTime: function () {
      this.vmData.startTime = null;
    },
    removeSchedule: function () {
      this.formDisabled = true;

      let headers = new Headers({
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      });

      fetch(`/api/schedule`, {
        method: "DELETE",
        headers: headers,
        body: JSON.stringify(this.vmData),
      }).then(() => {
        this.formDisabled = false;
        this.$emit("applied");
      });
    },
    updateSchedule: function () {
      this.formDisabled = true;

      let headers = new Headers({
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      });

      fetch(`/api/schedule`, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(this.vmData),
      }).then(() => {
        this.formDisabled = false;
        this.$emit("applied");
      });
    },
  },
  data() {
    return {
      formDisabled: false,
      vmData: null,
      formErrors: [],
      emptySchedule: null,
    };
  },
};
</script>