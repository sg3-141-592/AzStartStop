<template>
    <div v-if="errors.length > 0">
        <div v-for="error in errors" :key="error" class="notification is-warning">
            {{ error }}
        </div>
    </div>

    <FirstUseHelper v-if="subscriptions != null && subscriptions.length == 0"></FirstUseHelper>

    <div class="columns" v-if="subscriptions != null && subscriptions.length > 0">
        <div class="column is-6">
            <div class="field">
                <div class="control has-icons-left" v-if="subscriptions">
                    <div class="select is-fullwidth">
                        <select v-model="selectedSubscription">
                            <option v-for="subscription in subscriptions" :value="subscription.id" :key="subscription.id">
                                Subscription: {{ subscription.name }}
                            </option>
                        </select>
                    </div>
                    <div class="icon is-small is-left">
                        <i class="fa-solid fa-key"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <SubscriptionSummary :vms="vms" v-if="subscriptions != null && subscriptions.length > 0"></SubscriptionSummary>

    <div v-if="vms" class="table-container">
        <table class="table is-narrow is-fullwidth">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Sku</th>
                    <th>Resource Group</th>
                    <th>Est. Cost</th>
                    <th>Sched. Cost</th>
                    <th>Schedule</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="vm in vms" :key="vm">
                    <th>{{ vm.name }}</th>
                    <td>{{ shortenSku(vm.sku) }}</td>
                    <td>{{ vm.resourceGroup }}</td>
                    <td v-html="currencyText(vm.monthlyCost, currency)"></td>
                    <td v-html="currencyText(scheduleCost(vm), currency)"></td>
                    <td @click="scheduleVM(vm.id)"><a v-html="scheduleText(vm)"></a></td>
                </tr>
            </tbody>
        </table>
    </div>
    <progress v-else class="progress" max="100">15%</progress>

    <div v-if="selectedVM" class="modal is-active">
        <div class="modal-background"></div>
        <div class="modal-content">
            <div class="box">
                <SetSchedule @applied="selectedVM = null; loadVMs(selectedSubscription)" :vm="selectedVM"></SetSchedule>
            </div>
        </div>
        <button @click="selectedVM = null" class="modal-close is-large" aria-label="close"></button>
    </div>

</template>

<script>
import SetSchedule from '../components/SetSchedule.vue'
import SubscriptionSummary from '../components/SubscriptionSummary.vue'
import FirstUseHelper from '../components/FirstUseHelper.vue'
import { getScheduleRatio, getCurrencyText, getScheduleStr } from '../helper.js'

export default {  
    components: {
        SetSchedule,
        SubscriptionSummary,
        FirstUseHelper
    },
    mounted() {
        fetch(`/api/subscriptions`, {
            method: 'GET'
        })
            .then(response =>
                {
                    if(!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`${response.status} ${text}`)
                        })
                    }
                    return response.json()
                }
            )
            .then(data => {
                this.subscriptions = data;
                if(data.length > 0) {
                    // Default to the first returned subscription
                    this.selectedSubscription = data[0].id;
                }
            })
            .catch(err => {
                this.errors.push(err)
            })
    },
    watch: {
        selectedSubscription: function(val) {
            this.loadVMs(val)
        }
    },
    methods: {
        currencyText: getCurrencyText,
        scheduleStr: getScheduleStr,
        scheduleVM: function(id) {
            this.selectedVM = this.vms.find(element => element.id == id)
        },
        loadVMs: function(subscription_id) {
            this.vms = null
            // Find the id for the selected value
            fetch(`/api/vm?id=${subscription_id}`, {
                method: 'GET'
            })
                .then(response => {
                    if(!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`${response.status} ${text}`)
                        })
                    }
                    return response.json()
                })
                .then(data => {
                    this.vms = data.items,
                    this.currency = data.currency
                })
                .catch(err => {
                    this.errors.push(err)
                })
        },
        shortenSku: function(name) {
            // Make sku names shorted to make them display better on mobile
            name = name.replace("Standard", "Std")
            return name
        },
        scheduleCost: function(vm) {
            if(vm.stopTime == null || vm.startTime == null) {
                return null
            }
            let scheduledCost = vm.monthlyCost * getScheduleRatio(vm)
            return scheduledCost
        },
        scheduleText: function(vm) {
            if (vm.stopTime == null) {
                return `<i class="fa-solid fa-square-plus"></i> Add Schedule`
            } else {
                let dayString = this.scheduleStr(vm.daysOfWeek)
                if (vm.startTime == null) {
                    return `<i class="fa-solid fa-pencil"></i> ${vm.stopTime} ${dayString}`
                }
                return `<i class="fa-solid fa-pencil"></i> ${vm.startTime} - ${vm.stopTime} ${dayString}`
            }
        }
    },
    data() {
        return {
            selectedSubscription: null,
            selectedVM: null,
            vms: null,
            subscriptions: null,
            errors: [],
            currency: null
        }
    }
}
</script>
