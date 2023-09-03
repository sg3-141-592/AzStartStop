<template>
    <div class="box helper-background">
        <div class="icon-text">
            <span class="icon">
                <i class="fas fa-exclamation-triangle"></i>
            </span>
            <span>Az. Start Stop can't see any Subscriptions</span>
        </div>
        <br>
        <p>To start managing your resources to you need to assign the Az. Start Stop Managed Identity "Virtual Machine Contributor" and "Cost Management Reader" roles.</p>
        <br>
        <p>You can find this in the resource group you deploy Az. Start Stop to, and provide access like in the image below.</p>
        <br>
        <img :src="require('@/assets/add-role-assignment.png')">
    </div>
</template>

<style scoped>

.helper-background {
    background-color: white;
}

</style>