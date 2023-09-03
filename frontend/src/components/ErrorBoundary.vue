<template>
    <div>
        <slot
            v-if="(err.length > 0)"
            name="error"
            v-bind:err="err"
            v-bind:vm="vm"
            v-bind:info="info"
            >
                <div v-for="e in err" :key="e" class="notification is-warning">
                    {{ e }}
                </div>
        </slot>
        <slot v-else></slot>
    </div>
</template>

<script>
export default {
    name: "error-boundary",
    props: {
        stopPropagation: Boolean
    },
    data() {
        return {
            err: [],
            vm: null,
            info: null
        }
    },
    errorCaptured(err, vm, info) {
        this.err.push(err)
        this.vm = vm
        this.info = info
        return !this.stopPropagation
    }
};
</script>