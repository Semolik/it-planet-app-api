<template>
    <page-block title="Frienda - сброс пароля" max-width="400px">
        <div class="reset-password-content">
            <div class="info">Пароль должен содержать не менее 8 символов</div>
            <UInput
                v-model="password"
                placeholder="Пароль"
                type="password"
                size="lg"
            />
            <UInput
                v-model="passwordRepeat"
                placeholder="Повторите пароль"
                type="password"
                size="lg"
            />
            <UButton
                size="lg"
                :disabled="!passwordCorrect"
                @click="resetPassword"
            >
                Сбросить пароль
            </UButton>
            <div class="result" v-if="loading">
                <Icon name="svg-spinners:180-ring" />
            </div>
            <div class="result" v-else-if="isError">
                Ошибка при сбросе пароля
            </div>
            <div class="result" v-else-if="changed">Пароль успешно изменен</div>
        </div>
    </page-block>
</template>
<script setup>
const { apiBase } = useRuntimeConfig().public;
const {
    query: { token },
} = useRoute();
const loading = ref(false);
const isError = ref(false);
const password = ref("");
const passwordRepeat = ref("");
const passwordCorrect = computed(
    () => password.value.length >= 8 && password.value === passwordRepeat.value
);
const changed = ref(false);
const resetPassword = async () => {
    if (!passwordCorrect.value || loading.value) return;
    isError.value = false;
    loading.value = true;
    const { error } = await useFetch(`${apiBase}/auth/reset-password`, {
        method: "POST",
        body: { token, password },
    });
    isError.value = !!error.value;
    loading.value = false;
    changed.value = !isError.value;
};
</script>
<style lang="scss">
.reset-password-content {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 10px;

    .result {
        position: absolute;
        inset: 0;
        border-radius: 15px;
        background-color: hsl(0, 0%, 95%);
        z-index: 5;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
}
</style>
