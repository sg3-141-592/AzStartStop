<template>
    <h1 class="title">Settings</h1><p>Release 1.3-preview, November 2023</p>
    <hr />
    <div class="field">
        <label class="label">Timezone</label>
        <div class="control is-expanded" v-if="timezones">
            <div class="select is-fullwidth">
                <select v-model="selectedTimezone">
                    <option v-for="timezone in timezones" :key="timezone[0]" :value="timezone[0]">{{ timezone[0] }} {{ timezone[1] }}</option>
                </select>
            </div>
        </div>
    </div>
    <div class="field">
        <label class="label">Currency</label>
        <div class="control is-expanded" v-if="currencies">
            <div class="select is-fullwidth">
                <select v-model="selectedCurrency">
                    <option v-for="currencyDescription, currencyCode in currencies" :key="currencyCode" :value="currencyCode">{{ currencyCode }} - {{ currencyDescription }}</option>
                </select>
            </div>
        </div>
    </div>
    <div class="field is-grouped is-grouped-right">
        <div class="control">
            <button @click="setTimezone(); setCurrency();" class="button is-primary">
                <i class="fa-solid fa-floppy-disk"></i>&nbsp;Save
            </button>
        </div>
    </div>
</template>

<script>
export default {
    emits: ["applied"],
    mounted() {
        fetch(`/api/timezone`, {
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
                this.timezones = data.timezones;
                this.selectedTimezone = data.currentTimezone;
            })
        
        fetch(`/api/currencies`, {
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
                this.currencies = data.currencies;
                this.selectedCurrency = data.currentCurrency;
            })
    },
    methods: {
        setTimezone: function() {
            let headers = new Headers({
                Accept: "application/json, text/plain, */*",
                "Content-Type": "application/json",
            });

            fetch(`/api/timezone`, {
                method: "POST",
                headers: headers,
                body: JSON.stringify({
                    Timezone: this.selectedTimezone
                })
            }).then(() => {
                this.$emit("applied");
            });
        },
        setCurrency: function() {
            let headers = new Headers({
                Accept: "application/json, text/plain, */*",
                "Content-Type": "application/json",
            });

            fetch(`/api/currencies`, {
                method: "POST",
                headers: headers,
                body: JSON.stringify({
                    Currency: this.selectedCurrency
                })
            }).then(() => {
                this.$emit("applied");
            });
        },
    },
    data() {
        return {
            timezones: null,
            selectedTimezone: null,
            currencies: null,
            selectedCurrency: null
        }
    }
}
</script>