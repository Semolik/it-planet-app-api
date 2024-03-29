<template>
    <div class="page">
        <slot></slot>
    </div>
</template>
<script setup></script>
<style lang="scss">
body,
#__nuxt {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    min-height: 100vh;
}
.page {
    width: 100%;
    height: 100vh;
    padding: 20px;
    display: flex;
    background-color: white;
    justify-content: center;
    align-items: center;

    @media (max-width: 800px) {
        padding: 10px;
    }
}
*,
*:before,
*:after {
    box-sizing: border-box;
    transition: color 0.2s, background-color 0.2s, border-color 0.2s,
        opacity 0.2s;
    font-family: "Jost", sans-serif;
}
</style>
