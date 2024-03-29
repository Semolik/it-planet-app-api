<template>
    <div class="page-block">
        <div class="title" v-if="title">
            {{ title }}
        </div>
        <slot></slot>
    </div>
</template>
<script setup>
defineProps({
    title: String,
});
</script>
<style lang="scss" scoped>
.page-block {
    width: 100%;
    max-width: 400px;
    padding: 20px;
    background-color: hsl(0, 0%, 95%);
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    position: relative;

    .title {
        font-size: 20px;
        text-align: center;
    }
}
</style>
