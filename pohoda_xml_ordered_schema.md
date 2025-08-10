# Pohoda XML – Ordered Schema (podle golden vzorků)

Pořadí uzlů odpovídá přesně vybraným vzorkům. Sloupec **Typ** je dopočítán přes všechny poskytnuté XML (CONST/VAR).

## vch:voucher → voucherHeader

| Relativní XPath | Typ | Příklad | #unikátních |
|---|---|---|---|
| `vch:voucherType` | CONST | `receipt` | 1 |
| `vch:cashAccount` | CONST | `` | 1 |
| `vch:number` | CONST | `` | 1 |
| `vch:date` | VAR | `2025-06-03` | 5 |
| `vch:datePayment` | VAR | `2025-06-03` | 5 |
| `vch:dateTax` | VAR | `2025-06-03` | 5 |
| `vch:accounting` | CONST | `` | 1 |
| `vch:classificationVAT` | CONST | `` | 1 |
| `vch:text` | VAR | `Tržby hotově Bar & Grill` | 5 |
| `vch:myIdentity` | CONST | `` | 1 |
| `vch:centre` | CONST | `` | 1 |
| `vch:lock2` | CONST | `false` | 1 |
| `vch:markRecord` | CONST | `false` | 1 |
| `vch:labels` | CONST | `` | 1 |
| `vch:cashAccount/typ:ids` | VAR | `BaG` | 4 |
| `vch:number/typ:numberRequested` | VAR | `BaGP00005` | 6 |
| `vch:accounting/typ:ids` | VAR | `211000/602112` | 3 |
| `vch:classificationVAT/typ:ids` | CONST | `UD` | 1 |
| `vch:myIdentity/typ:address` | CONST | `` | 1 |
| `vch:centre/typ:ids` | VAR | `1` | 4 |
| `vch:labels/typ:label` | CONST | `` | 1 |
| `vch:myIdentity/typ:address/typ:company` | CONST | `Lipno Gastro Services s.r.o.` | 1 |
| `vch:myIdentity/typ:address/typ:city` | CONST | `Praha` | 1 |
| `vch:myIdentity/typ:address/typ:street` | CONST | `Radlická` | 1 |
| `vch:myIdentity/typ:address/typ:number` | CONST | `751/113e` | 1 |
| `vch:myIdentity/typ:address/typ:zip` | CONST | `158 00` | 1 |
| `vch:myIdentity/typ:address/typ:ico` | CONST | `17126240` | 1 |
| `vch:myIdentity/typ:address/typ:dic` | CONST | `CZ17126240` | 1 |
| `vch:labels/typ:label/typ:ids` | CONST | `Zelená` | 1 |

## vch:voucher → voucherDetail

| Relativní XPath | Typ | Příklad | #unikátních |
|---|---|---|---|
| `vch:voucherItem` | CONST | `` | 1 |
| `vch:voucherItem/vch:text` | VAR | `Spropitné` | 5 |
| `vch:voucherItem/vch:quantity` | CONST | `1.0` | 1 |
| `vch:voucherItem/vch:coefficient` | CONST | `1.0` | 1 |
| `vch:voucherItem/vch:payVAT` | CONST | `false` | 1 |
| `vch:voucherItem/vch:rateVAT` | VAR | `high` | 3 |
| `vch:voucherItem/vch:discountPercentage` | CONST | `0.0` | 1 |
| `vch:voucherItem/vch:homeCurrency` | CONST | `` | 1 |
| `vch:voucherItem/vch:accounting` | CONST | `` | 1 |
| `vch:voucherItem/vch:PDP` | CONST | `false` | 1 |
| `vch:voucherItem/vch:classificationVAT` | CONST | `` | 1 |
| `vch:voucherItem/vch:homeCurrency/typ:unitPrice` | VAR | `0` | 16 |
| `vch:voucherItem/vch:homeCurrency/typ:price` | VAR | `0` | 16 |
| `vch:voucherItem/vch:homeCurrency/typ:priceVAT` | VAR | `0` | 12 |
| `vch:voucherItem/vch:homeCurrency/typ:priceSum` | VAR | `0` | 16 |
| `vch:voucherItem/vch:accounting/typ:ids` | VAR | `211000/602110` | 9 |
| `vch:voucherItem/vch:classificationVAT/typ:ids` | CONST | `UN` | 1 |
| `vch:voucherItem/vch:classificationVAT/typ:classificationVATType` | CONST | `nonSubsume` | 1 |

## vch:voucher → voucherSummary

| Relativní XPath | Typ | Příklad | #unikátních |
|---|---|---|---|
| `vch:roundingDocument` | CONST | `math2one` | 1 |
| `vch:roundingVAT` | CONST | `none` | 1 |
| `vch:calculateVAT` | CONST | `false` | 1 |
| `vch:typeCalculateVATInclusivePrice` | CONST | `VATNewMethod` | 1 |
| `vch:homeCurrency` | CONST | `` | 1 |
| `vch:homeCurrency/typ:priceNone` | VAR | `0` | 5 |
| `vch:homeCurrency/typ:priceLow` | VAR | `0` | 6 |
| `vch:homeCurrency/typ:priceLowVAT` | VAR | `0` | 6 |
| `vch:homeCurrency/typ:priceLowSum` | VAR | `0` | 6 |
| `vch:homeCurrency/typ:priceHigh` | VAR | `234.75` | 6 |
| `vch:homeCurrency/typ:priceHighVAT` | VAR | `106.74` | 6 |
| `vch:homeCurrency/typ:priceHighSum` | VAR | `284.05` | 6 |
| `vch:homeCurrency/typ:round` | CONST | `` | 1 |
| `vch:homeCurrency/typ:round/typ:priceRound` | CONST | `0` | 1 |

## inv:invoice (kartou) → invoiceHeader

| Relativní XPath | Typ | Příklad | #unikátních |
|---|---|---|---|
| `inv:invoiceType` | CONST | `receivable` | 1 |
| `inv:number` | CONST | `` | 1 |
| `inv:symVar` | VAR | `250900107` | 10 |
| `inv:date` | VAR | `2025-06-03` | 5 |
| `inv:dateTax` | VAR | `2025-06-03` | 5 |
| `inv:dateAccounting` | VAR | `2025-06-03` | 5 |
| `inv:dateDue` | VAR | `2025-06-03` | 5 |
| `inv:accounting` | CONST | `` | 1 |
| `inv:classificationVAT` | CONST | `` | 1 |
| `inv:text` | VAR | `Tržby Bar & Gril - Voucher` | 9 |
| `inv:myIdentity` | CONST | `` | 1 |
| `inv:paymentType` | CONST | `` | 1 |
| `inv:account` | CONST | `` | 1 |
| `inv:symConst` | CONST | `0308` | 1 |
| `inv:centre` | CONST | `` | 1 |
| `inv:liquidation` | CONST | `` | 1 |
| `inv:lock2` | CONST | `false` | 1 |
| `inv:markRecord` | CONST | `false` | 1 |
| `inv:number/typ:numberRequested` | VAR | `250900107` | 10 |
| `inv:accounting/typ:ids` | VAR | `315000/602112` | 2 |
| `inv:classificationVAT/typ:ids` | CONST | `UDA5` | 1 |
| `inv:myIdentity/typ:address` | CONST | `` | 1 |
| `inv:paymentType/typ:ids` | VAR | `Plat.kartou` | 2 |
| `inv:paymentType/typ:paymentType` | VAR | `cheque` | 2 |
| `inv:account/typ:ids` | CONST | `RBCZ` | 1 |
| `inv:account/typ:accountNo` | CONST | `7415855002` | 1 |
| `inv:account/typ:bankCode` | CONST | `5500` | 1 |
| `inv:centre/typ:ids` | VAR | `1` | 4 |
| `inv:liquidation/typ:date` | VAR | `2025-06-04` | 7 |
| `inv:myIdentity/typ:address/typ:company` | CONST | `Lipno Gastro Services s.r.o.` | 1 |
| `inv:myIdentity/typ:address/typ:city` | CONST | `Praha` | 1 |
| `inv:myIdentity/typ:address/typ:street` | CONST | `Radlická` | 1 |
| `inv:myIdentity/typ:address/typ:number` | CONST | `751/113e` | 1 |
| `inv:myIdentity/typ:address/typ:zip` | CONST | `158 00` | 1 |
| `inv:myIdentity/typ:address/typ:ico` | CONST | `17126240` | 1 |
| `inv:myIdentity/typ:address/typ:dic` | CONST | `CZ17126240` | 1 |

## inv:invoice (kartou) → invoiceDetail

| Relativní XPath | Typ | Příklad | #unikátních |
|---|---|---|---|
| `inv:invoiceItem` | CONST | `` | 1 |
| `inv:invoiceItem/inv:text` | VAR | `0% Service Charge` | 3 |
| `inv:invoiceItem/inv:quantity` | CONST | `1.0` | 1 |
| `inv:invoiceItem/inv:coefficient` | CONST | `1.0` | 1 |
| `inv:invoiceItem/inv:payVAT` | CONST | `false` | 1 |
| `inv:invoiceItem/inv:rateVAT` | VAR | `high` | 3 |
| `inv:invoiceItem/inv:discountPercentage` | CONST | `0.0` | 1 |
| `inv:invoiceItem/inv:homeCurrency` | CONST | `` | 1 |
| `inv:invoiceItem/inv:accounting` | CONST | `` | 1 |
| `inv:invoiceItem/inv:PDP` | CONST | `false` | 1 |
| `inv:invoiceItem/inv:classificationVAT` | CONST | `` | 1 |
| `inv:invoiceItem/inv:homeCurrency/typ:unitPrice` | VAR | `0` | 25 |
| `inv:invoiceItem/inv:homeCurrency/typ:price` | VAR | `0` | 25 |
| `inv:invoiceItem/inv:homeCurrency/typ:priceVAT` | VAR | `0` | 20 |
| `inv:invoiceItem/inv:homeCurrency/typ:priceSum` | VAR | `0` | 25 |
| `inv:invoiceItem/inv:accounting/typ:ids` | VAR | `315000/602110` | 9 |
| `inv:invoiceItem/inv:classificationVAT/typ:ids` | CONST | `UN` | 1 |
| `inv:invoiceItem/inv:classificationVAT/typ:classificationVATType` | CONST | `nonSubsume` | 1 |

## inv:invoice (kartou) → invoiceSummary

| Relativní XPath | Typ | Příklad | #unikátních |
|---|---|---|---|
| `inv:roundingDocument` | VAR | `math2one` | 2 |
| `inv:roundingVAT` | CONST | `none` | 1 |
| `inv:typeCalculateVATInclusivePrice` | CONST | `VATNewMethod` | 1 |
| `inv:homeCurrency` | CONST | `` | 1 |
| `inv:homeCurrency/typ:priceNone` | VAR | `0` | 6 |
| `inv:homeCurrency/typ:priceLow` | VAR | `0` | 10 |
| `inv:homeCurrency/typ:priceLowVAT` | VAR | `0` | 10 |
| `inv:homeCurrency/typ:priceLowSum` | VAR | `0` | 10 |
| `inv:homeCurrency/typ:priceHigh` | VAR | `10553.08` | 10 |
| `inv:homeCurrency/typ:priceHighVAT` | VAR | `130.95` | 10 |
| `inv:homeCurrency/typ:priceHighSum` | VAR | `12769.23` | 10 |
| `inv:homeCurrency/typ:round` | CONST | `` | 1 |
| `inv:homeCurrency/typ:round/typ:priceRound` | VAR | `-0.03` | 3 |

## inv:invoice (voucher) → invoiceHeader

| Relativní XPath | Typ | Příklad | #unikátních |
|---|---|---|---|
| `inv:invoiceType` | CONST | `receivable` | 1 |
| `inv:number` | CONST | `` | 1 |
| `inv:symVar` | VAR | `250900107` | 10 |
| `inv:date` | VAR | `2025-06-03` | 5 |
| `inv:dateTax` | VAR | `2025-06-03` | 5 |
| `inv:dateAccounting` | VAR | `2025-06-03` | 5 |
| `inv:dateDue` | VAR | `2025-06-03` | 5 |
| `inv:accounting` | CONST | `` | 1 |
| `inv:classificationVAT` | CONST | `` | 1 |
| `inv:text` | VAR | `Tržby Bar & Gril - Voucher` | 9 |
| `inv:myIdentity` | CONST | `` | 1 |
| `inv:paymentType` | CONST | `` | 1 |
| `inv:account` | CONST | `` | 1 |
| `inv:symConst` | CONST | `0308` | 1 |
| `inv:centre` | CONST | `` | 1 |
| `inv:liquidation` | CONST | `` | 1 |
| `inv:lock2` | CONST | `false` | 1 |
| `inv:markRecord` | CONST | `false` | 1 |
| `inv:number/typ:numberRequested` | VAR | `250900107` | 10 |
| `inv:accounting/typ:ids` | VAR | `315000/602112` | 2 |
| `inv:classificationVAT/typ:ids` | CONST | `UDA5` | 1 |
| `inv:myIdentity/typ:address` | CONST | `` | 1 |
| `inv:paymentType/typ:ids` | VAR | `Plat.kartou` | 2 |
| `inv:paymentType/typ:paymentType` | VAR | `cheque` | 2 |
| `inv:account/typ:ids` | CONST | `RBCZ` | 1 |
| `inv:account/typ:accountNo` | CONST | `7415855002` | 1 |
| `inv:account/typ:bankCode` | CONST | `5500` | 1 |
| `inv:centre/typ:ids` | VAR | `1` | 4 |
| `inv:liquidation/typ:date` | VAR | `2025-06-04` | 7 |
| `inv:myIdentity/typ:address/typ:company` | CONST | `Lipno Gastro Services s.r.o.` | 1 |
| `inv:myIdentity/typ:address/typ:city` | CONST | `Praha` | 1 |
| `inv:myIdentity/typ:address/typ:street` | CONST | `Radlická` | 1 |
| `inv:myIdentity/typ:address/typ:number` | CONST | `751/113e` | 1 |
| `inv:myIdentity/typ:address/typ:zip` | CONST | `158 00` | 1 |
| `inv:myIdentity/typ:address/typ:ico` | CONST | `17126240` | 1 |
| `inv:myIdentity/typ:address/typ:dic` | CONST | `CZ17126240` | 1 |

## inv:invoice (voucher) → invoiceDetail

| Relativní XPath | Typ | Příklad | #unikátních |
|---|---|---|---|
| `inv:invoiceItem` | CONST | `` | 1 |
| `inv:invoiceItem/inv:text` | VAR | `0% Service Charge` | 3 |
| `inv:invoiceItem/inv:quantity` | CONST | `1.0` | 1 |
| `inv:invoiceItem/inv:coefficient` | CONST | `1.0` | 1 |
| `inv:invoiceItem/inv:payVAT` | CONST | `false` | 1 |
| `inv:invoiceItem/inv:rateVAT` | VAR | `high` | 3 |
| `inv:invoiceItem/inv:discountPercentage` | CONST | `0.0` | 1 |
| `inv:invoiceItem/inv:homeCurrency` | CONST | `` | 1 |
| `inv:invoiceItem/inv:accounting` | CONST | `` | 1 |
| `inv:invoiceItem/inv:PDP` | CONST | `false` | 1 |
| `inv:invoiceItem/inv:classificationVAT` | CONST | `` | 1 |
| `inv:invoiceItem/inv:homeCurrency/typ:unitPrice` | VAR | `0` | 25 |
| `inv:invoiceItem/inv:homeCurrency/typ:price` | VAR | `0` | 25 |
| `inv:invoiceItem/inv:homeCurrency/typ:priceVAT` | VAR | `0` | 20 |
| `inv:invoiceItem/inv:homeCurrency/typ:priceSum` | VAR | `0` | 25 |
| `inv:invoiceItem/inv:accounting/typ:ids` | VAR | `315000/602110` | 9 |
| `inv:invoiceItem/inv:classificationVAT/typ:ids` | CONST | `UN` | 1 |
| `inv:invoiceItem/inv:classificationVAT/typ:classificationVATType` | CONST | `nonSubsume` | 1 |

## inv:invoice (voucher) → invoiceSummary

| Relativní XPath | Typ | Příklad | #unikátních |
|---|---|---|---|
| `inv:roundingDocument` | VAR | `math2one` | 2 |
| `inv:roundingVAT` | CONST | `none` | 1 |
| `inv:typeCalculateVATInclusivePrice` | CONST | `VATNewMethod` | 1 |
| `inv:homeCurrency` | CONST | `` | 1 |
| `inv:homeCurrency/typ:priceNone` | VAR | `0` | 6 |
| `inv:homeCurrency/typ:priceLow` | VAR | `0` | 10 |
| `inv:homeCurrency/typ:priceLowVAT` | VAR | `0` | 10 |
| `inv:homeCurrency/typ:priceLowSum` | VAR | `0` | 10 |
| `inv:homeCurrency/typ:priceHigh` | VAR | `10553.08` | 10 |
| `inv:homeCurrency/typ:priceHighVAT` | VAR | `130.95` | 10 |
| `inv:homeCurrency/typ:priceHighSum` | VAR | `12769.23` | 10 |
| `inv:homeCurrency/typ:round` | CONST | `` | 1 |
| `inv:homeCurrency/typ:round/typ:priceRound` | VAR | `-0.03` | 3 |
