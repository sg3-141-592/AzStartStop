<template>
    <!-- Helper to show messages to users about new releases and features -->
    <div v-if="message" class="notification is-link">
        <button class="delete" @click="closeMessage();"></button>
        <div class="content" v-html="message"></div>
    </div>
</template>

<script>
export default {
    mounted() {
        // Check if the user has already cleared the current message
        var clearedMessage = localStorage.getItem('clearedMessage')
        fetch(`https://startstopvmsresources.z33.web.core.windows.net/messages.html`, {
            method: 'GET'
        })
            .then(response =>
                {
                    if(!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`${response.status} ${text}`)
                        })
                    }
                    return response.text()
                }
            )
            .then(data => {
                // If the user hasn't cleared the current message display it
                if(clearedMessage != data) {
                    this.message = data
                }
            })
    },
    methods: {
        closeMessage: function () {
            localStorage.clearedMessage = this.message;
            this.message = null;
        }
    },
    data() {
        return {
            message: null
        }
    }
}
</script>