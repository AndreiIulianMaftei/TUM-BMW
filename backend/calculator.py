from backend.models import (
    ComprehensiveAnalysis, TAMMetrics, SAMMetrics, SOMMetrics,
    ROIMetrics, TurnoverMetrics, VolumeMetrics, UnitEconomics,
    EBITMetrics, COGSMetrics, MarketPotential, Variable, Formula
)
from typing import Dict, Any

def calculate_complete_analysis(extracted: Dict[str, Any]) -> ComprehensiveAnalysis:
    print("\n" + "-"*80)
    print("🧮 CALCULATOR: Starting complete analysis")
    print("-"*80)

    try:
        # -------------------- INPUT EXTRACTION --------------------
        project_name = extracted.get('project_name', 'Business Analysis')
        project_type = extracted.get('project_type', 'revenue')
        annual_value = extracted.get('annual_revenue_or_savings')
        fleet_size = extracted.get('fleet_size_or_units')
        price_per_unit = extracted.get('price_per_unit')
        streams = extracted.get('stream_values', []) or []
        total_streams = sum(s for s in streams if s) if streams else None
        dev_cost = extracted.get('development_cost', 0)
        growth = extracted.get('growth_rate', 5.0)
        royalty = extracted.get('royalty_percentage', 0.0)
        take_rate = extracted.get('take_rate', 10.0)
        market_cov = extracted.get('market_coverage', 50.0)
        categories = extracted.get('number_of_product_categories')

        print("📥 Input values:")
        print(f"   Project: {project_name}")
        print(f"   Type: {project_type.upper()}")
        print(f"   Annual value: €{annual_value:,}" if annual_value else "   Annual value: None")
        print(f"   Fleet size: {fleet_size:,}" if fleet_size else "   Fleet size: None")
        print(f"   Price/unit: €{price_per_unit}" if price_per_unit else "   Price/unit: None")
        print(f"   Streams: {streams}")
        print(f"   Dev cost: €{dev_cost:,}" if dev_cost else "   Dev cost: 0")
        print(f"   Growth: {growth}%")
        print(f"   Royalty: {royalty}%")

        # Defaults
        if dev_cost is None: dev_cost = 0
        if growth is None: growth = 5.0
        if royalty is None: royalty = 0.0
        if take_rate is None: take_rate = 10.0
        if market_cov is None: market_cov = 50.0
        if categories is not None and categories <= 0: categories = None

        is_savings = project_type in ['savings', 'cost_savings', 'efficiency']
        is_royalty = project_type == 'royalty'

        # -------------------- EXPLICIT OVERRIDES --------------------
        # Support explicit market size overrides extracted directly from the document
        explicit_tam = extracted.get('explicit_tam')
        explicit_sam = extracted.get('explicit_sam')
        explicit_som = extracted.get('explicit_som')
        overrides_used = []
        if explicit_tam is not None or explicit_sam is not None or explicit_som is not None:
            print("\n🔍 Explicit market size values detected:")
            if explicit_tam is not None:
                print(f"   • TAM override: €{explicit_tam:,.0f}")
            if explicit_sam is not None:
                print(f"   • SAM override: €{explicit_sam:,.0f}")
            if explicit_som is not None:
                print(f"   • SOM override: €{explicit_som:,.0f}")

        # --- Heuristic: infer categories for royalty if annual_value looks like royalty revenue ---
        if is_royalty and annual_value and fleet_size and price_per_unit and royalty and take_rate and market_cov and not categories:
            try:
                base = fleet_size * price_per_unit * (market_cov/100.0) * (take_rate/100.0) * (royalty/100.0)
                inferred = round(annual_value / base) if base > 0 else 0
                if inferred >= 1:
                    categories = inferred
                    print(f"   🔍 Inferred product categories: {categories}")
            except Exception:
                pass

        print("\n💡 Calculating TAM, SAM, SOM (explicit overrides checked first)...")
        if is_savings:
            if explicit_tam is not None or explicit_sam is not None or explicit_som is not None:
                tam = explicit_tam if explicit_tam is not None else (explicit_som if explicit_som is not None else (annual_value or (total_streams or 0)))
                sam = explicit_sam if explicit_sam is not None else tam
                som = explicit_som if explicit_som is not None else (annual_value or (total_streams or sam))
                overrides_used.extend([n for n,v in [('TAM',explicit_tam),('SAM',explicit_sam),('SOM',explicit_som)] if v is not None])
                print(f"   ✅ Savings overrides applied: {', '.join(overrides_used)}")
            else:
                som = annual_value or (total_streams or 0)
                tam = som
                sam = som
                print(f"   Provided validated annual savings = €{som:,.0f} (used as TAM=SAM=SOM)")
        elif is_royalty:
            if explicit_tam is not None:
                tam = explicit_tam
                overrides_used.append('TAM')
                print(f"   ✅ Explicit TAM override used: €{tam:,.0f}")
                sam = explicit_sam if explicit_sam is not None else tam * (market_cov/100.0)
                if explicit_sam is not None:
                    overrides_used.append('SAM')
                som = explicit_som if explicit_som is not None else sam * (take_rate/100.0)
                if explicit_som is not None:
                    overrides_used.append('SOM')
            else:
                # Maintain original inference logic only when TAM isn't explicitly provided
                if fleet_size and price_per_unit and categories:
                    tam = fleet_size * categories * price_per_unit
                    sam = tam * (market_cov/100.0)
                    gross_gmv_captured = sam * (take_rate/100.0)
                    if annual_value and royalty:
                        expected_royalty = gross_gmv_captured * (royalty/100.0)
                        som = gross_gmv_captured
                        print(f"   TAM = {fleet_size:,} × {categories} × €{price_per_unit} = €{tam:,.0f}")
                        print(f"   SAM = TAM × {market_cov}% = €{sam:,.0f}")
                        print(f"   Gross GMV captured (SOM base) = SAM × {take_rate}% = €{som:,.0f}")
                        if abs(expected_royalty - annual_value) > 1:
                            print(f"   ⚠️ Provided annual royalty (€{annual_value:,.0f}) != computed (€{expected_royalty:,.0f}), using provided value for revenue")
                    else:
                        som = gross_gmv_captured
                        annual_value = som * (royalty/100.0)
                else:
                    if annual_value and royalty:
                        som = annual_value / (royalty/100.0)
                        sam = som / (take_rate/100.0) if take_rate else som
                        tam = sam / (market_cov/100.0) if market_cov else sam
                        print(f"   Royalty revenue provided: €{annual_value:,.0f} -> Gross GMV (SOM) €{som:,.0f}")
                        print(f"   Back-computed SAM: €{sam:,.0f} | TAM: €{tam:,.0f}")
                    else:
                        tam = annual_value or (fleet_size * price_per_unit if (fleet_size and price_per_unit) else 0)
                        sam = tam * (market_cov/100.0)
                        som = sam * (take_rate/100.0)
                        print(f"   Fallback TAM=€{tam:,.0f} SAM=€{sam:,.0f} SOM=€{som:,.0f}")
            # Apply explicit SAM/SOM overrides if TAM wasn't explicit but they were
            if explicit_tam is None:
                if explicit_sam is not None:
                    sam = explicit_sam
                    overrides_used.append('SAM')
                    print(f"   ✅ Explicit SAM override used: €{sam:,.0f}")
                if explicit_som is not None:
                    som = explicit_som
                    overrides_used.append('SOM')
                    print(f"   ✅ Explicit SOM override used: €{som:,.0f}")
        else:
            if explicit_tam is not None or explicit_sam is not None or explicit_som is not None:
                tam = explicit_tam if explicit_tam is not None else (fleet_size * price_per_unit if (fleet_size and price_per_unit) else (annual_value or 0))
                sam = explicit_sam if explicit_sam is not None else tam * (market_cov/100.0)
                som = explicit_som if explicit_som is not None else (sam * (take_rate/100.0))
                overrides_used.extend([n for n,v in [('TAM',explicit_tam),('SAM',explicit_sam),('SOM',explicit_som)] if v is not None])
                print(f"   ✅ Revenue overrides applied: {', '.join(overrides_used)}")
            else:
                if fleet_size and price_per_unit:
                    base_tam = fleet_size * price_per_unit
                    if annual_value and annual_value < base_tam:
                        tam = base_tam
                        sam = tam * (market_cov/100.0)
                        som = annual_value
                        print(f"   Realized annual revenue provided (€{annual_value:,.0f}) used as SOM; TAM=€{tam:,.0f} SAM=€{sam:,.0f}")
                    else:
                        tam = base_tam if not annual_value else annual_value
                        sam = tam * (market_cov/100.0)
                        som = sam * (take_rate/100.0)
                        print(f"   TAM=€{tam:,.0f} SAM=€{sam:,.0f} SOM=€{som:,.0f}")
                elif annual_value:
                    tam = sam = som = annual_value
                    print(f"   Annual value treated as realized SOM = €{som:,.0f} (no unit base available)")
                else:
                    tam = sam = som = 0
                    print("   No market inputs available -> zeros for TAM/SAM/SOM")

        if overrides_used:
            print(f"   🔁 Overrides precedence applied for: {', '.join(overrides_used)}")

        # At this point tam/sam/som set according to revised semantics

        # Unit / economics
        if is_savings:
            units = fleet_size or 0
            cogs_per_unit = 0
            print("\n💡 SAVINGS PROJECT")
            print(f"   Annual achievable savings (Y1): €{som:,.0f}")
            # If dev_cost absent, estimate 10% of annual validated savings (more conservative than 15%)
            if dev_cost == 0 and som:
                dev_cost = som * 0.10
                print(f"   Estimated implementation cost (10% of validated savings): €{dev_cost:,.0f}")
        else:
            if is_royalty:
                if fleet_size and (categories or 1):
                    # Accessory transactions count (not royalty revenue) -> volume basis
                    units = fleet_size * (categories or 1) * (market_cov/100.0) * (take_rate/100.0)
                else:
                    units = som / price_per_unit if price_per_unit else 0
                cogs_per_unit = 0
                print(f"\n💡 Units (royalty accessory transactions): {int(units):,}")
            else:
                if fleet_size and price_per_unit and som:
                    units = som / price_per_unit
                elif fleet_size:
                    units = fleet_size * (market_cov/100.0) * (take_rate/100.0)
                else:
                    units = 0
                if price_per_unit is None:
                    price_per_unit = (annual_value / fleet_size) if (annual_value and fleet_size) else 500
                cogs_per_unit = price_per_unit * 0.25
                print(f"\n💡 Units (sales/subscription): {int(units):,}")
                print(f"   Price/unit: €{price_per_unit:.2f} | COGS/unit: €{cogs_per_unit:.2f} | Margin/unit: €{price_per_unit - cogs_per_unit:.2f}")

        years = [2025, 2026, 2027, 2028, 2029]
        tam_numbers = {str(y): tam * ((1 + growth/100.0) ** (y - 2025)) for y in years}
        sam_numbers = {str(y): sam * ((1 + growth/100.0) ** (y - 2025)) for y in years}
        som_numbers = {str(y): som * ((1 + growth/100.0) ** (y - 2025)) for y in years}

        yearly_costs: Dict[str, Dict[str, Any]] = {}
        yearly_revenue: Dict[str, float] = {}
        print("\n💡 Year-by-year breakdown:")

        if is_savings:
            for i, year in enumerate(years):
                annual_savings = som * ((1 + growth/100.0) ** i)
                dev = dev_cost if i == 0 else 0
                maintenance = (dev_cost * 0.20) if i > 0 else 0
                ops_cost = annual_savings * 0.05
                change_mgmt = annual_savings * 0.02
                admin = annual_savings * 0.01
                total_cost = dev + maintenance + ops_cost + change_mgmt + admin
                net_savings = annual_savings - total_cost
                yearly_costs[str(year)] = {
                    'projected_volume': int(units) if units else 0,
                    'one_time_development': dev,
                    'customer_acquisition': change_mgmt,
                    'distribution_operations': ops_cost,
                    'after_sales': admin + maintenance,
                    'total_cogs': 0,
                    'cogs_per_unit': 0,
                    'total_cost': total_cost,
                    'currency': 'EUR'
                }
                yearly_revenue[str(year)] = annual_savings
                print(f"   {year}: Savings=€{annual_savings:,.0f} | Impl=€{total_cost:,.0f} | Net=€{net_savings:,.0f}")
            volume_numbers = {str(y): int(units) for y in years}
        else:
            volume_numbers = {str(y): int(units * ((1 + growth/100.0) ** (y - 2025))) for y in years}
            for i, year in enumerate(years):
                vol = units * ((1 + growth/100.0) ** i)
                dev = dev_cost if i == 0 else 0
                if is_royalty and royalty > 0:
                    if annual_value:  # annual_value is already royalty revenue (not to be reduced again)
                        revenue = annual_value * ((1 + growth/100.0) ** i)
                        gross_gmv_year = revenue / (royalty/100.0)
                    else:
                        gross_gmv_year = som * ((1 + growth/100.0) ** i)
                        revenue = gross_gmv_year * (royalty / 100.0)
                    cac = vol * 12
                    ops = vol * 6
                    after_sales = vol * 4
                    total_cogs = 0
                    cogs_per_unit = 0
                    total_cost = dev + cac + ops + after_sales
                else:
                    total_cogs = vol * cogs_per_unit
                    ops = vol * 15
                    cac = vol * 10
                    after_sales = vol * 5
                    revenue = price_per_unit * vol
                    total_cost = dev + total_cogs + ops + cac + after_sales
                yearly_costs[str(year)] = {
                    'projected_volume': int(vol),
                    'one_time_development': dev,
                    'customer_acquisition': cac,
                    'distribution_operations': ops,
                    'after_sales': after_sales,
                    'total_cogs': total_cogs,
                    'cogs_per_unit': cogs_per_unit,
                    'total_cost': total_cost,
                    'currency': 'EUR'
                }
                yearly_revenue[str(year)] = revenue
                profit = revenue - total_cost
                print(f"   {year}: Vol={int(vol):,} | Rev=€{revenue:,.0f} | Cost=€{total_cost:,.0f} | Profit=€{profit:,.0f}")

        total_revenue = sum(yearly_revenue.values())
        total_cost = sum(y['total_cost'] for y in yearly_costs.values())
        total_volume = sum(y['projected_volume'] for y in yearly_costs.values())
        net_profit = total_revenue - total_cost
        roi_pct = (net_profit / total_cost * 100) if total_cost > 0 else 0
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        if is_savings:
            print("\n💡 5-Year Totals (SAVINGS PROJECT):")
            print(f"   Total Achievable Savings: €{total_revenue:,.0f}")
            print(f"   Total Implementation & Ops Cost: €{total_cost:,.0f}")
            print(f"   Net Savings: €{net_profit:,.0f}")
            print(f"   ROI: {roi_pct:.1f}% | Efficiency: {profit_margin:.1f}%")
        else:
            print("\n💡 5-Year Totals:")
            print(f"   Total Revenue: €{total_revenue:,.0f}")
            print(f"   Total Cost: €{total_cost:,.0f}")
            print(f"   Net Profit: €{net_profit:,.0f}")
            print(f"   ROI: {roi_pct:.1f}% | Margin: {profit_margin:.1f}%")

        roi_numbers = {}
        ebit_numbers = {}
        for year in years:
            rev = yearly_revenue[str(year)]
            cost = yearly_costs[str(year)]['total_cost']
            profit = rev - cost
            roi_numbers[str(year)] = (profit / cost * 100) if cost > 0 else 0
            ebit_numbers[str(year)] = profit

        break_even_months = 60
        cumulative = -dev_cost
        for i, year in enumerate(years, start=1):
            annual_net = yearly_revenue[str(year)] - yearly_costs[str(year)]['total_cost']
            monthly_net = annual_net / 12.0
            for month in range(12):
                cumulative += monthly_net
                if cumulative >= 0:
                    break_even_months = (i - 1) * 12 + month
                    break
            if cumulative >= 0:
                break
        print(f"   Break-even: {break_even_months} months")
        print("-"*80)

        if is_savings:
            identified_vars = [
                Variable(name="TAM", value=f"€{tam:,.0f}", description="Annual addressable savings potential"),
                Variable(name="SAM", value=f"€{sam:,.0f}", description=f"Serviceable savings ({market_cov}% capacity)"),
                Variable(name="SOM", value=f"€{som:,.0f}", description=f"Achievable annual savings ({take_rate}% execution)")
            ]
            identified_vars.extend([
                Variable(name="Annual Savings (Y1)", value=f"€{som:,.0f}", description="Year 1 achievable savings"),
                Variable(name="Implementation Cost", value=f"€{dev_cost:,.0f}", description="Estimated upfront implementation"),
                Variable(name="Growth Rate", value=f"{growth}%", description="Annual savings growth assumption"),
                Variable(name="5-Year Net Savings", value=f"€{net_profit:,.0f}", description="Cumulative net after costs"),
                Variable(name="ROI", value=f"{roi_pct:.1f}%", description="Net savings / total cost")
            ])
            formulas = [
                Formula(name="SAM Calculation", formula="SAM = TAM × Capacity %", calculation=f"€{tam:,.0f} × {market_cov}% = €{sam:,.0f}"),
                Formula(name="SOM Calculation", formula="SOM = SAM × Execution %", calculation=f"€{sam:,.0f} × {take_rate}% = €{som:,.0f}"),
                Formula(name="Implementation Cost", formula="Dev (est) = Y1 Savings × 15%", calculation=f"€{som:,.0f} × 15% = €{dev_cost:,.0f}"),
                Formula(name="Net Savings", formula="Net = Gross Savings (5Y) - Total Cost (5Y)", calculation=f"€{total_revenue:,.0f} - €{total_cost:,.0f} = €{net_profit:,.0f}"),
                Formula(name="ROI", formula="ROI = Net ÷ Total Cost", calculation=f"€{net_profit:,.0f} ÷ €{total_cost:,.0f} = {roi_pct:.1f}%")
            ]
        else:
            identified_vars = [
                Variable(name="TAM", value=f"€{tam:,.0f}", description="Total addressable market"),
                Variable(name="SAM", value=f"€{sam:,.0f}", description=f"Serviceable market ({market_cov}% of TAM)"),
                Variable(name="SOM", value=f"€{som:,.0f}", description=f"Obtainable market ({take_rate}% of SAM)"),
                Variable(name="Units (Y1)", value=f"{int(units):,}", description="Projected Year 1 volume")
            ]
            if price_per_unit:
                identified_vars.extend([
                    Variable(name="Price per Unit", value=f"€{price_per_unit:,.2f}", description="Average price"),
                    Variable(name="COGS per Unit", value=f"€{cogs_per_unit:,.2f}", description="Cost of goods (est 25%)"),
                ])
            identified_vars.extend([
                Variable(name="Growth Rate", value=f"{growth}%", description="Annual growth"),
                Variable(name="ROI", value=f"{roi_pct:.1f}%", description="Return on total cost"),
                Variable(name="Profit Margin", value=f"{profit_margin:.1f}%", description="Net / Revenue")
            ])
            formulas = [
                Formula(name="SAM", formula="SAM = TAM × Coverage %", calculation=f"€{tam:,.0f} × {market_cov}% = €{sam:,.0f}"),
                Formula(name="SOM", formula="SOM = SAM × Take Rate %", calculation=f"€{sam:,.0f} × {take_rate}% = €{som:,.0f}"),
                Formula(name="Units", formula="Units = SOM ÷ Price", calculation=f"€{som:,.0f} ÷ €{price_per_unit} = {int(units):,}" if price_per_unit else "Price/unit missing"),
                Formula(name="Net Profit", formula="Net = Revenue - Total Cost", calculation=f"€{total_revenue:,.0f} - €{total_cost:,.0f} = €{net_profit:,.0f}"),
                Formula(name="ROI", formula="ROI = Net ÷ Total Cost", calculation=f"€{net_profit:,.0f} ÷ €{total_cost:,.0f} = {roi_pct:.1f}%")
            ]

        return ComprehensiveAnalysis(
            project_name=project_name,
            project_type=project_type,
            tam=TAMMetrics(
                description_of_public=("Total addressable savings opportunity" if is_savings else "Total addressable market"),
                market_size=tam,
                growth_rate=growth,
                numbers=tam_numbers,
                justification=("Derived from annual savings potential" if is_savings else "Derived from fleet × price assumptions"),
                insight=(f"Annual savings potential €{tam/1_000_000:.2f}M" if is_savings else f"Market size €{tam/1_000_000:.2f}M"),
                confidence=85
            ),
            sam=SAMMetrics(
                description_of_public=("Serviceable savings" if is_savings else "Serviceable available market"),
                market_size=sam,
                numbers=sam_numbers,
                justification=("Capacity & organizational constraints" if is_savings else "Market coverage assumption"),
                insight=f"SAM €{sam/1_000_000:.2f}M", confidence=80, penetration_rate=market_cov
            ),
            som=SOMMetrics(
                description_of_public=("Achievable annual savings" if is_savings else "Obtainable market share"),
                market_share=take_rate,
                revenue_potential=som,
                numbers=som_numbers,
                justification=("Execution realization rate" if is_savings else "Take rate assumption"),
                insight=f"SOM €{som/1_000_000:.2f}M", confidence=75, customer_acquisition_cost=0
            ),
            roi=ROIMetrics(
                revenue=total_revenue, cost=total_cost, roi_percentage=roi_pct,
                numbers=roi_numbers, payback_period_months=break_even_months,
                insight=f"ROI {roi_pct:.1f}% | Break-even {break_even_months}m", confidence=80
            ),
            turnover=TurnoverMetrics(
                total_revenue=total_revenue/5, yoy_growth=growth, numbers=yearly_revenue,
                insight=f"Avg annual {'savings' if is_savings else 'revenue'} €{(total_revenue/5)/1_000_000:.2f}M", confidence=75
            ),
            volume=VolumeMetrics(
                units_sold=int(round(units)), numbers=volume_numbers,
                insight=(f"Context fleet size: {fleet_size:,}" if is_savings and fleet_size else f"Projected volume Y1: {int(units):,}"),
                confidence=70
            ),
            unit_economics=UnitEconomics(
                unit_revenue=price_per_unit, unit_cost=cogs_per_unit,
                margin=(price_per_unit - cogs_per_unit) if (price_per_unit and not is_savings) else 0,
                margin_percentage=profit_margin, ltv_cac_ratio=5.0,
                insight=(f"Savings efficiency {profit_margin:.1f}%" if is_savings else f"Net margin {profit_margin:.1f}%"),
                confidence=75
            ),
            ebit=EBITMetrics(
                revenue=total_revenue/5, operating_expense=total_cost/5,
                ebit_margin=net_profit/5, ebit_percentage=profit_margin, numbers=ebit_numbers,
                insight=f"EBIT margin {profit_margin:.1f}%", confidence=75
            ),
            cogs=COGSMetrics(
                material=0, labor=0, overheads=0, total_cogs=cogs_per_unit * (units if not is_savings else 0),
                cogs_percentage=((cogs_per_unit / price_per_unit)*100 if price_per_unit and cogs_per_unit else 0),
                numbers={str(y): yearly_costs[str(y)]['total_cogs'] for y in years},
                insight=f"COGS per unit €{cogs_per_unit:.2f}", confidence=70
            ),
            market_potential=MarketPotential(
                market_size=tam, penetration=take_rate, growth_rate=growth, numbers=tam_numbers,
                insight="Healthy growth outlook", confidence=80
            ),
            yearly_cost_breakdown=yearly_costs,
            seven_year_summary={
                'total_cost_2024_2030': total_cost,
                'total_volume_2024_2030': int(total_volume),
                'average_cost_per_unit': (total_cost / total_volume) if total_volume else 0,
                'currency': 'EUR'
            },
            total_estimated_cost_summary={
                'total_revenue_5_years': total_revenue,
                'total_cost_5_years': total_cost,
                'net_profit_5_years': net_profit,
                'roi_percentage': roi_pct,
                'profit_margin_percentage': profit_margin,
                'break_even_months': float(break_even_months)
            },
            executive_summary=(
                f"{project_name}: Annual savings potential €{tam/1_000_000:.2f}M, achievable €{som/1_000_000:.2f}M; ROI {roi_pct:.1f}%." if is_savings
                else f"{project_name}: TAM €{tam/1_000_000:.2f}M, SOM €{som/1_000_000:.2f}M; ROI {roi_pct:.1f}%."
            ),
            value_market_potential_text=(
                f"Savings path modeled with capacity {market_cov}% and execution {take_rate}%. Break-even {break_even_months} months; cumulative net €{net_profit/1_000_000:.2f}M." if is_savings
                else f"Market path with coverage {market_cov}% and take rate {take_rate}%. Break-even {break_even_months} months; net €{net_profit/1_000_000:.2f}M."),
            business_assumptions=[
                f"Growth {growth}%",
                f"Take rate {take_rate}%",
                f"Annual savings Y1 €{som:,.0f}" if is_savings else f"Avg price €{price_per_unit:.0f}" if price_per_unit else "Price assumption applied"
            ],
            improvement_recommendations=(
                ["Prioritize high-yield streams", "Embed tracking early", "Phase rollout to reduce risk"] if is_savings
                else ["Validate pricing elasticity", "Optimize CAC per channel", "Monitor unit margin drift"]
            ),
            identified_variables=identified_vars,
            formulas=formulas
        )
    except Exception as e:
        print("\n❌ CALCULATOR ERROR")
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())
        raise
