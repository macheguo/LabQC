<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/shared/PageHeader.vue'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import { Button } from '@/components/ui/button'
const { t } = useI18n()
const test = ref(false)
console.log('SettingsView imports OK')
</script>
<template>
  <div class="settings-page">
    <PageHeader :title="t('settings.title')" :subtitle="t('settings.subtitle')" />
    <StatusBadge :status="test ? 'success' : 'inactive'" label="Test" />
    <Button @click="test=!test">Toggle</Button>
    <p>All components work</p>
  </div>
</template>
