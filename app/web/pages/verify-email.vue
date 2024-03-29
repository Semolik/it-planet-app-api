<template>
    <page-block title="Frienda - подтверждение почты">
        <div class="block">
            <Icon name="svg-spinners:180-ring" v-if="loading" />
            <div v-else-if="isError">Ошибка при подтверждении почты</div>
            <div v-else>Почта успешно подтверждена</div>
        </div>
    </page-block>
</template>
<script setup>
const { apiBase } = useRuntimeConfig().public;
const {
    query: { token },
} = useRoute();
const loading = ref(true);
const isError = ref(false);
onMounted(async () => {
    isError.value = false;
    loading.value = true;
    const { error } = await useFetch(`${apiBase}/auth/verify`, {
        method: "POST",
        body: { token },
    });
    isError.value = !!error.value;
    loading.value = false;
});
</script>
<style lang="scss">
.block {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
    background-color: rgba($color: #000000, $alpha: 0.05);
    border-radius: 15px;
}
</style>
