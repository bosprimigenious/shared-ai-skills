# 成本与容量决策

## 三个候选方案

必须同时计算：全小时制、全包日、小时 pilot + 包日正式窗口。固定费用包括 API、持久存储和传输；不要把 API 费用塞进 GPU 单价。

```text
hourly_expected = hourly_price × (pilot_hours + formal_hours)
                + fixed_costs
                + reacquire_probability × reacquire_impact

daily_expected  = daily_price × ceil((pilot_hours + formal_hours) / 24)
                + fixed_costs

hybrid_expected = hourly_price × pilot_hours
                + daily_price × ceil(formal_hours / 24)
                + fixed_costs
```

`reacquire_impact` 包含重新构建、重新下载、重复测试、延期和错过提交窗口的估计损失。它不是虚构账单；没有依据时分低/中/高三个场景，不填一个伪精确值。

运行：

```bash
python3 scripts/plan_capacity.py \
  --hourly-price 7 \
  --daily-price 120 \
  --pilot-hours 4 \
  --formal-hours 22 \
  --api-cost 150 \
  --reacquire-probability 0.4 \
  --reacquire-impact 300
```

## 推荐规则

- 代码、数据、模型或恢复尚未跑通：只允许本地/小卡或小时 pilot。
- pilot 通过且正式窗口超过价格盈亏点：优先包日或预约容量。
- 纯小时制表面便宜，但关机后高概率无卡时，将容量风险纳入总成本。
- 包日不是必须跑满；空闲时长换取补测能力。是否值得取决于容量风险和截止日期。
- 若平台提供预约时段、保留实例或可迁移持久盘，优先于盲目包日。
- 小 GPU 只证明功能、显存趋势和恢复流程；正式性能、峰值显存和时间门必须在目标 GPU 协议上重跑。

## 成本台账

至少记录：时间、provider、实例/GPU、价格单位、运行角色、训练/评分/空闲/恢复、API、存储、累计、预算上限、下一止损点。报销额度、获批金额、实际账单和可报销金额分列。
