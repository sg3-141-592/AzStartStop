<template>
    <footer class="footer">
        <div class="content">
            <p>
                Free open source virtual machine cost management. Install now from <a href="https://github.com/sg3-141-592/AzStartStop"><strong>Github - AzStartStop</strong></a>.
            </p>
            <p>
                Coming to Azure Marketplace soon.
            </p>
            <p v-if="signedUp == false">
                Want to be notified of new features and improvements in the tool ? Sign up here
            </p>
            <p v-else>Thanks for signing up !!!</p>
            <div v-if="signedUp == false" class="field has-addons has-addons-centered signup">
                <div class="control is-expanded">
                    <input v-model="userEmail" class="input is-primary" type="email" placeholder="hello@world.com"
                        :disabled="signUpDisabled" />
                </div>
                <div class="control">
                    <button @click="signUp()" class="button is-info" :disabled="signUpDisabled">
                        Sign-up
                    </button>
                </div>
            </div>
        </div>
    </footer>
</template>

<script>
export default {
    methods: {
        signUp: function () {
            this.signUpDisabled = true
            let headers = new Headers({
                Accept: "application/json, text/plain, */*",
                "Content-Type": "application/json",
            });
            fetch(`/api/signup`, {
                method: "POST",
                headers: headers,
                body: JSON.stringify({ email: this.userEmail }),
            }).then(() => {
                this.signedUp = true
            });
        },
    },
    data() {
        return {
            userEmail: null,
            signUpDisabled: false,
            signedUp: false,
        };
    }
}
</script>

<style scoped>
.signup {
    width: 100%;
    max-width: 500px;
}
</style>