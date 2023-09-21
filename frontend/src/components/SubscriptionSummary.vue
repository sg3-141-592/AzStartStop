<template>
    <div v-if="vms" class="box pink-background">
        <div class="columns is-mobile">
            <div class="column">
                <div v-if="expanded === false">
                    <a class="has-text-white has-text-weight-bold is-size-4">{{ calcVMSpend() == 0 ? "--" : currencyText(calcVMSpend(), this.currency) }}</a>
                    <a class="has-text-white"> last month</a>
                </div>
            </div>
            <div class="column is-narrow">
                <p class="has-text-right" @click="expandClicked()">
                    <span class="icon is-medium">
                        <span class="fa-stack fa-sm">
                            <i class="fa-regular fa-circle fa-inverse fa-stack-2x"></i>
                            <div v-if="expanded === true">
                                <i class="fas fa-angles-up fa-stack-1x fa-inverse"></i>
                            </div>
                            <div v-else>
                                <i class="fas fa-angles-down fa-stack-1x fa-inverse"></i>
                            </div>
                        </span>
                    </span>
                </p>
            </div>
        </div>

        <div v-if="expanded === true" class="columns">
            <div class="column">
                <h2 class="has-text-white is-underlined">VM Spend</h2>
                <a class="has-text-white has-text-weight-bold is-size-4">{{ calcVMSpend() == 0 ? "--" : currencyText(calcVMSpend(), this.currency) }}</a><a
                    class="has-text-white"> last month</a>
                <p><a class="has-text-white has-text-weight-bold is-size-4">{{ currencyText(calcEstSpend(), this.monthlyCurrency) }}</a><a
                        class="has-text-white"> est. next month</a></p>
                <!-- <p class="has-text-white"><i class="fa-solid fa-arrow-trend-down"></i> $1,092 month</p> -->
            </div>
            <div class="column">
                <h2 class="has-text-white is-underlined">VM Hours</h2>
                <p><a class="has-text-white has-text-weight-bold is-size-4">{{ calcVMHours().scheduledHours }}/{{
                    calcVMHours().hoursTotal }}</a><a class="has-text-white"> scheduled hours</a></p>
                <p>
                    <progress class="progress is-primary progress-spacing" :value="calcVMHours().scheduledHours"
                        :max="calcVMHours().hoursTotal">15%</progress>
                </p>
                <!-- <p class="has-text-white"><i class="fa-solid fa-arrow-trend-down"></i> 322 hours</p> -->
            </div>
        </div>
    </div>
</template>

<script>
import { getScheduleRatio, getCurrencyText } from '../helper.js'

export default {
    props: ['vms'],
    watch: {
        vms: function(newVms) {
            // Try and get the bill currency
            if(newVms != null && newVms.length > 0) {
                this.currency = newVms[0].actualCostCurrency
            }
            // Try and get the estimate currency
            if(newVms != null && newVms.length > 0) {
                this.monthlyCurrency = newVms[0].monthlyCostCurrency
            }
        }
    },
    methods: {
        currencyText: getCurrencyText,
        expandClicked() {
            this.expanded = !this.expanded;
        },
        calcVMHours() {
            let hoursTotal = 0
            let scheduledHours = 0
            this.vms.forEach(element => {
                hoursTotal += 30 * 24
                if (element.stopTime) {
                    let vmRatio = getScheduleRatio(element)
                    scheduledHours += 30 * 24 * vmRatio
                } else {
                    scheduledHours += 30 * 24
                }
            });
            scheduledHours = Math.round(scheduledHours, 0)
            return { scheduledHours, hoursTotal }
        },
        calcEstSpend() {
            let estCost = 0.0
            this.vms.forEach(element => {
                if (element.stopTime) {
                    estCost += element.monthlyCost * getScheduleRatio(element)
                } else {
                    estCost += element.monthlyCost
                }
            })
            return estCost
        },
        calcVMSpend() {
            let totalSpend = 0
            this.vms.forEach(element => {
                totalSpend += element.actualCost
            })
            return totalSpend
        }
    },
    data() {
        return {
            expanded: false,
            currency: null,
            monthlyCurrency: null,
        }
    }
}
</script>

<style scoped>
.progress-spacing {
    margin-top: 5px;
}
</style>