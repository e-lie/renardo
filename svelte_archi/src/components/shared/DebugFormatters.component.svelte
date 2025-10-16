<script lang="ts">
  import { useLocalization, useDateTimeFormatters, useNumberFormatters } from '@/localization'

  // expose component properties
  export let show = false

  // get what we need from useLocalization:
  const { currentLocale } = useLocalization()

  $: dateTimeFormatter = (dateStyle: string = 'long', timeStyle: string = '') => {
    return useDateTimeFormatters($currentLocale).dateTime(dateStyle, timeStyle)
  }
  $: dayNames = () => {
    return useDateTimeFormatters($currentLocale)
      .dayNames()
      .map((o) => o.name)
      .join(', ')
  }
  $: monthNames = () => {
    return useDateTimeFormatters($currentLocale)
      .monthNames()
      .map((o) => o.name)
      .join(', ')
  }

  $: wholeNumberFormatter = () => {
    return useNumberFormatters($currentLocale).whole()
  }
  $: decimalNumberFormatter = () => {
    return useNumberFormatters($currentLocale).decimal()
  }
  $: currencyNumberFormatter = (currency: string = 'USD') => {
    return useNumberFormatters($currentLocale).currency(currency)
  }
  $: percentNumberFormatter = () => {
    return useNumberFormatters($currentLocale).percent()
  }
</script>

{#if show}
  <div>
    <h3>Debugging formatters:</h3>
    <div>Whole: {wholeNumberFormatter().format(123456789.321654)}</div>
    <div>Decimal: {decimalNumberFormatter().format(123456789.321654)}</div>
    <div>percent: {percentNumberFormatter().format(1254.987654)}</div>

    <div>currency (USD): {currencyNumberFormatter().format(123456789.321654)}</div>
    <div>currency (CAD): {currencyNumberFormatter('CAD').format(123456789.321654)}</div>
    <div>currency (EUR): {currencyNumberFormatter('EUR').format(123456789.321654)}</div>
    <div>currency (CNY): {currencyNumberFormatter('CNY').format(123456789.321654)}</div>
    <div>currency (JPY): {currencyNumberFormatter('JPY').format(123456789.321654)}</div>
    <div>currency (INR): {currencyNumberFormatter('INR').format(123456789.321654)}</div>
    <div>currency (CHF): {currencyNumberFormatter('CHF').format(123456789.321654)}</div>

    <div>date-time (default): {dateTimeFormatter().format(new Date())}</div>
    <div>date-time (full): {dateTimeFormatter('full').format(new Date())}</div>
    <div>date-time (full + long time): {dateTimeFormatter('full', 'long').format(new Date())}</div>

    <div>day names: {dayNames()}</div>
    <div>month names: {monthNames()}</div>
  </div>
{/if}
