<template>
  <section class="hero is-small is-link">
    <div class="hero-body">
      <p class="title"><i class="fa-solid fa-clock"></i> Az. Start Stop</p>
    </div>
    <div class="hero-foot">
      <nav class="tabs is-right">
        <ul>
          <li>
            <a @click="settingsView = true">
              <span class="icon is-small"><i class="fa-solid fa-gear" aria-hidden="true"></i></span>
              <span>Settings</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </section>
  <!-- Settings View -->
  <div v-if="settingsView" class="modal is-active">
    <div class="modal-background"></div>
    <div class="modal-content">
      <div class="box">
        <UpdateSettings @applied="settingsView = false; this.$router.go()"></UpdateSettings>
      </div>
      <button @click="settingsView = false" class="modal-close is-large" aria-label="close"></button>
    </div>
  </div>
  <!-- -->
  <section class="section">
    <UserMessage></UserMessage>
    <router-view />
  </section>
  <!-- -->
  <SignUp v-if="showSignUps"></SignUp>
</template>

<script>
import UpdateSettings from './components/UpdateSettings.vue'
import UserMessage from './components/UserMessage.vue'
import SignUp from './components/SignUp.vue'

export default {
  components: {
    UpdateSettings,
    UserMessage,
    SignUp
  },
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
      settingsView: false,
      showSignUps: false
    };
  },
};
</script>
