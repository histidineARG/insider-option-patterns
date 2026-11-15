# What the resolved SEC option cases actually did

Read 2026-11-13 from `data/sec_cases.json` and the named series in `optiondaily`. This file has no criminal-conviction flag. Complaints stay allegations. The resolved civil matters used here are the Kraft, Joy, Lantheus, and Maxar settled administrative findings, the Heinz, Audentes, and Calliditas settlement announcements, the Incyte civil verdict, the Bioverativ default judgment, and the Kaman partial consent judgments.

## The contracts, measured at the purchase

| Matter | Outcome | Calls named by the source | At purchase | Days to expiry | Open interest |
| --- | --- | --- | --- | ---: | --- |
| Heinz 2013-02-13 | Settlement announced | Series not extracted. The busiest call that day was the June 65 | Spot 60.47, delta 0.17, about 8% out of the money. Volume 2,593 against open interest 364 | 129 | The print was several times the existing open interest |
| Kraft 2015-03-23 | Settled findings | 100 of the June 67.5 | Spot 62.12, delta 0.20, 8.7% out of the money. Volume 361 | 88 | Open interest stayed near 20,200. One hundred contracts do not move it |
| Incyte 2016-08-18 | Civil verdict | 578 of the September 80, 82.5, and 85 | Spot 76.16, deltas 0.39, 0.31, 0.23, 5–12% out of the money | 29 | Open interest was unchanged on the trade date and rose the next session: 552 to 693, 162 to 329, 1,002 to 1,106 |
| Joy 2016-07-20 | Settled findings | 50 calls, strikes not extracted | Several strikes traded 20–106 contracts that day | 2 to 184 | Fifty contracts cannot be picked out of that tape |
| Bioverativ 2018-01-12 to 01-19 | Default judgment | 1,607 of the February 65, 70, and 75 | On January 12, spot 63.75, deltas 0.47, 0.27, 0.16, about 2–18% out of the money | 35 at the start, 28 at the end | The 75 strike went from 0 open interest on January 11 to 1,156 on the announcement |
| Kaman 2023-12-21 to 2024-01-18 | Partial consent | 618 of the March 30 | Spot about 22, strike 30, roughly 34% out of the money. Stored delta is 0.00 | About 57–85 | Open interest went from 23 to 528 |

Lantheus was 15 calls and Maxar was 2. Both are settled findings, and both are below what an end-of-day chain can attribute.

Incyte is not a purchase of the company being acquired. The calls were on a peer, and that peer rose about 8% into August 22, under the 15% jump line.

## What to carry into the screen

- The purchase is calls, one to three strikes, while the stock has not yet gapped.
- Moneyness at purchase is usually about 5–20% out of the money, delta about 0.15–0.40. Kaman was much further out, so a hard delta floor at 0.10 drops a resolved case.
- Expiry has to cover the announcement, but it is not short. Incyte and Bioverativ were about a month out. Heinz, Kraft, and Kaman were two to four months out. A 45-day maximum drops those three.
- Open interest in this table is the position entering the session. The increase from a purchase prints the next session. A rule that requires same-day open interest to rise will miss Incyte. A rule that stops the day before the announcement will also miss the confirmation of a purchase made that day, as with Kraft.
- Size decides whether the chain can see the case. Heinz, Bioverativ, and Kaman were large against the existing open interest. Kraft, Joy, Lantheus, and Maxar were not. Those small resolved cases are outside the reach of an aggregate screen, and a miss there is not evidence that the trade did not happen.
