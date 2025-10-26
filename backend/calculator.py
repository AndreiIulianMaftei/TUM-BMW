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
        project_name = extracted.get('project_name', 'Business Analysis')
        project_type = extracted.get('project_type', 'revenue')
        annual_value = extracted.get('annual_revenue_or_savings')
        fleet_size = extracted.get('fleet_size_or_units')
        price_per_unit = extracted.get('price_per_unit')
        streams = extracted.get('stream_values', [])
        dev_cost = extracted.get('development_cost', 0)
        growth = extracted.get('growth_rate', 5.0)
        royalty = extracted.get('royalty_percentage', 0.0)
        take_rate = extracted.get('take_rate', 10.0)
        market_cov = extracted.get('market_coverage', 50.0)
        
        print(f"📥 Input values:")
        print(f"   Project: {project_name}")
        print(f"   Type: {project_type.upper()}")
        print(f"   Annual value: €{annual_value:,}" if annual_value else "   Annual value: None")
        print(f"   Fleet size: {fleet_size:,}" if fleet_size else "   Fleet size: None")
        print(f"   Price/unit: €{price_per_unit}" if price_per_unit else "   Price/unit: None")
        print(f"   Streams: {streams}")
        print(f"   Dev cost: €{dev_cost:,}" if dev_cost else "   Dev cost: 0")
        print(f"   Growth: {growth}%")
        print(f"   Royalty: {royalty}%")
        
        if dev_cost is None:
            dev_cost = 0
        if growth is None:
            growth = 5.0
        if royalty is None:
            royalty = 0.0
        if take_rate is None:
            take_rate = 10.0
        if market_cov is None:
            market_cov = 50.0
        
        is_savings = project_type in ['savings', 'cost_savings', 'efficiency']
        
        print("\n💡 Calculating TAM...")
        tam = None
        total_streams = sum(s for s in streams if s) if streams else None
        
        if total_streams and total_streams > 0:
            tam = total_streams * 5
            print(f"   TAM from streams (€{total_streams:,} annual × 5 years): €{tam:,.0f}")
        elif annual_value:
            tam = annual_value * 5
            print(f"   TAM from annual value (€{annual_value:,} × 5 years): €{tam:,.0f}")
        elif fleet_size and price_per_unit:
            tam = fleet_size * price_per_unit
            print(f"   TAM from fleet × price ({fleet_size:,} × €{price_per_unit}): €{tam:,.0f}")
        else:
            tam = 50_000_000
            print(f"   TAM fallback: €{tam:,.0f}")
        
        if is_savings:
            sam_percent = 75.0
            som_percent = 70.0
            print(f"\n💡 Market segmentation (SAVINGS PROJECT):")
            print(f"   SAM: {sam_percent}% of TAM (organizational capacity to implement)")
            print(f"   SOM: {som_percent}% of SAM (realistic execution considering change management)")
            
            if dev_cost == 0:
                annual_savings = total_streams if total_streams else (annual_value or tam/5)
                dev_cost = annual_savings * 0.15
                print(f"   💡 Estimated development cost: €{dev_cost:,.0f} (15% of annual savings)")
                print(f"      Covers: feasibility studies, software dev, process implementation, training")
        else:
            sam_percent = 100.0
            som_percent = 80.0
            print(f"\n💡 Market segmentation (REVENUE PROJECT):")
            print(f"   SAM: {sam_percent}% of TAM (serviceable market)")
            print(f"   SOM: {som_percent}% of SAM (realistic market share)")
        
        sam = tam * (sam_percent / 100)
        som = sam * (som_percent / 100)
        
        print(f"\n💡 Market sizes:")
        print(f"   TAM: €{tam:,.0f}")
        print(f"   SAM: €{sam:,.0f}")
        print(f"   SOM: €{som:,.0f}")
        
        if is_savings:
            units = 0
            price_per_unit = 0
            cogs_per_unit = 0
            print(f"\n💡 SAVINGS PROJECT - No units/pricing model")
            print(f"   Annual savings (Year 1): €{som/5:,.0f}")
            print(f"   Implementation costs per year: minimal after setup")
        elif fleet_size and not price_per_unit:
            if annual_value and fleet_size:
                price_per_unit = annual_value / fleet_size
                print(f"   Price/unit calculated: €{price_per_unit:.2f}")
            else:
                price_per_unit = 500
                print(f"   Price/unit defaulted: €{price_per_unit}")
            
            if royalty > 0:
                units = fleet_size * (take_rate / 100) * (market_cov / 100)
                print(f"\n💡 Units (royalty model): {units:,.0f}")
                print(f"   Fleet: {fleet_size:,} × Take rate: {take_rate}% × Market: {market_cov}%")
            else:
                units = som / price_per_unit if price_per_unit > 0 else fleet_size
                print(f"\n💡 Units (sales model): {units:,.0f}")
                print(f"   SOM / Price per unit: €{som:,.0f} / €{price_per_unit}")
            
            cogs_per_unit = price_per_unit * 0.25
            print(f"\n💡 Unit economics:")
            print(f"   Price/unit: €{price_per_unit:.2f}")
            print(f"   COGS/unit: €{cogs_per_unit:.2f} (25% of price)")
            print(f"   Margin/unit: €{price_per_unit - cogs_per_unit:.2f}")
        else:
            if price_per_unit is None:
                price_per_unit = 500
            if fleet_size is None:
                fleet_size = 10000
                
            if royalty > 0:
                units = fleet_size * (take_rate / 100) * (market_cov / 100)
                print(f"\n💡 Units (royalty model): {units:,.0f}")
            else:
                units = som / price_per_unit if price_per_unit > 0 else fleet_size
                print(f"\n💡 Units (sales model): {units:,.0f}")
            
            cogs_per_unit = price_per_unit * 0.25
            print(f"\n💡 Unit economics:")
            print(f"   Price/unit: €{price_per_unit:.2f}")
            print(f"   COGS/unit: €{cogs_per_unit:.2f} (25% of price)")
            print(f"   Margin/unit: €{price_per_unit - cogs_per_unit:.2f}")
        
        years = [2025, 2026, 2027, 2028, 2029]
        
        print(f"\n💡 Calculating 5-year projections...")
        tam_numbers = {str(y): tam * ((1 + growth/100) ** (y - 2025)) for y in years}
        sam_numbers = {str(y): sam * ((1 + growth/100) ** (y - 2025)) for y in years}
        som_numbers = {str(y): som * ((1 + growth/100) ** (y - 2025)) for y in years}
        
        yearly_costs = {}
        yearly_revenue = {}
        
        print(f"\n💡 Year-by-year breakdown:")
        
        if is_savings:
            base_savings = som / 5
            for i, year in enumerate(years):
                annual_savings = base_savings * ((1 + growth/100) ** i)
                
                dev = dev_cost if i == 0 else 0
                maintenance = dev_cost * 0.15 if i > 0 else 0
                process_cost = annual_savings * 0.05
                
                total_cost = dev + maintenance + process_cost
                net_savings = annual_savings - total_cost
                
                yearly_costs[str(year)] = {
                    'projected_volume': 0,
                    'one_time_development': dev,
                    'customer_acquisition': 0,
                    'distribution_operations': maintenance,
                    'after_sales': process_cost,
                    'total_cogs': 0,
                    'cogs_per_unit': 0,
                    'total_cost': total_cost,
                    'currency': 'EUR'
                }
                
                yearly_revenue[str(year)] = annual_savings
                
                print(f"   {year}: Savings=€{annual_savings:,.0f} | Implementation=€{total_cost:,.0f} | Net=€{net_savings:,.0f}")
            
            volume_numbers = {str(y): 0 for y in years}
            
        else:
            volume_numbers = {str(y): units * ((1 + growth/100) ** (y - 2025)) for y in years}
            
            for i, year in enumerate(years):
                vol = units * ((1 + growth/100) ** i)
                
                dev = dev_cost if i == 0 else 0
                total_cogs = vol * cogs_per_unit
                ops = vol * 15
                cac = vol * 10
                after_sales = vol * 5
                
                if royalty > 0:
                    revenue = price_per_unit * vol * (royalty / 100)
                    total_cost = dev + cac + ops + after_sales
                else:
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
            print(f"\n💡 5-Year Totals (SAVINGS PROJECT):")
            print(f"   Total Savings: €{total_revenue:,.0f}")
            print(f"   Total Implementation Cost: €{total_cost:,.0f}")
            print(f"   Net Savings: €{net_profit:,.0f}")
            print(f"   ROI: {roi_pct:.1f}%")
            print(f"   Savings Efficiency: {profit_margin:.1f}%")
        else:
            print(f"\n💡 5-Year Totals:")
            print(f"   Total Revenue: €{total_revenue:,.0f}")
            print(f"   Total Cost: €{total_cost:,.0f}")
            print(f"   Net Profit: €{net_profit:,.0f}")
            print(f"   ROI: {roi_pct:.1f}%")
            print(f"   Profit Margin: {profit_margin:.1f}%")
        
        roi_numbers = {}
        ebit_numbers = {}
        
        for year in years:
            y_str = str(year)
            rev = yearly_revenue[y_str]
            cost = yearly_costs[y_str]['total_cost']
            profit = rev - cost
            
            roi_numbers[y_str] = (profit / cost * 100) if cost > 0 else 0
            ebit_numbers[y_str] = profit
        
        # Calculate break-even point more accurately
        break_even_months = 60  # Default to 5 years if never breaks even
        cumulative = -dev_cost  # Start with initial investment as negative
        
        for i, year in enumerate(years, start=1):
            annual_net = yearly_revenue[str(year)] - yearly_costs[str(year)]['total_cost']
            monthly_net = annual_net / 12
            
            # Check each month of the year
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
                Variable(name="TAM", value=f"€{tam:,.0f}", description="Total addressable savings over 5 years"),
                Variable(name="SAM", value=f"€{sam:,.0f}", description=f"Serviceable savings ({sam_percent}% of TAM due to organizational capacity)"),
                Variable(name="SOM", value=f"€{som:,.0f}", description=f"Obtainable savings ({som_percent}% of SAM after execution risk)"),
                Variable(name="Annual Savings (Y1)", value=f"€{som/5:,.0f}", description="First year achievable savings"),
                Variable(name="Implementation Cost", value=f"€{dev_cost:,.0f}", description="Upfront investment for feasibility, software, process setup"),
                Variable(name="Growth Rate", value=f"{growth}%", description="Annual savings growth rate"),
                Variable(name="5-Year Net Savings", value=f"€{net_profit:,.0f}", description="Total savings minus implementation costs"),
                Variable(name="ROI", value=f"{roi_pct:.1f}%", description="Return on implementation investment"),
            ]
            
            # For formulas, handle None values safely
            # Use TAM/5 as the display value for annual calculations
            annual_value_display = tam / 5
            
            formulas = [
                Formula(
                    name="TAM Calculation",
                    formula="TAM = Annual value × 5 years",
                    calculation=f"€{annual_value_display:,.0f} × 5 = €{tam:,.0f}"
                ),
                Formula(
                    name="SAM Calculation",
                    formula="SAM = TAM × Organizational Capacity %",
                    calculation=f"€{tam:,.0f} × {sam_percent}% = €{sam:,.0f}"
                ),
                Formula(
                    name="SOM Calculation",
                    formula="SOM = SAM × Execution Success Rate %",
                    calculation=f"€{sam:,.0f} × {som_percent}% = €{som:,.0f}"
                ),
                Formula(
                    name="Annual Savings (Year 1)",
                    formula="Annual Savings = SOM ÷ 5 years",
                    calculation=f"€{som:,.0f} ÷ 5 = €{som/5:,.0f}"
                ),
                Formula(
                    name="Implementation Cost Estimate",
                    formula="Dev Cost = Annual Savings × 15% (software + process + training)",
                    calculation=f"€{annual_value_display:,.0f} × 15% = €{dev_cost:,.0f}"
                ),
                Formula(
                    name="Net Savings Calculation",
                    formula="Net Savings = Total Gross Savings - Implementation Costs",
                    calculation=f"€{total_revenue:,.0f} - €{total_cost:,.0f} = €{net_profit:,.0f}"
                ),
                Formula(
                    name="ROI Calculation",
                    formula="ROI % = (Net Savings ÷ Implementation Cost) × 100",
                    calculation=f"(€{net_profit:,.0f} ÷ €{total_cost:,.0f}) × 100 = {roi_pct:.1f}%"
                ),
            ]
        else:
            identified_vars = [
                Variable(name="TAM", value=f"€{tam:,.0f}", description="Total addressable market over 5 years"),
                Variable(name="SAM", value=f"€{sam:,.0f}", description=f"Serviceable available market ({sam_percent}% of TAM)"),
                Variable(name="SOM", value=f"€{som:,.0f}", description=f"Serviceable obtainable market ({som_percent}% of SAM)"),
                Variable(name="Price per Unit", value=f"€{price_per_unit:,.2f}", description="Average selling price per unit"),
                Variable(name="COGS per Unit", value=f"€{cogs_per_unit:,.2f}", description="Cost of goods sold per unit (25% of price)"),
                Variable(name="Units (Year 1)", value=f"{int(units):,}", description="Projected volume in first year"),
                Variable(name="Growth Rate", value=f"{growth}%", description="Annual growth rate"),
                Variable(name="Gross Margin", value=f"{((price_per_unit - cogs_per_unit)/price_per_unit*100):.1f}%", description="Profit margin per unit"),
            ]
            
            formulas = [
                Formula(
                    name="TAM Calculation",
                    formula="TAM = Annual Revenue × 5 years OR Fleet Size × Price per Unit",
                    calculation=f"€{total_streams if total_streams else annual_value:,.0f} × 5 = €{tam:,.0f}" if (total_streams or annual_value) else f"{fleet_size:,} × €{price_per_unit} = €{tam:,.0f}"
                ),
                Formula(
                    name="SOM Calculation",
                    formula="SOM = TAM × SAM % × Market Share %",
                    calculation=f"€{tam:,.0f} × {sam_percent}% × {som_percent}% = €{som:,.0f}"
                ),
                Formula(
                    name="Units Calculation",
                    formula="Units = SOM ÷ Price per Unit",
                    calculation=f"€{som:,.0f} ÷ €{price_per_unit} = {int(units):,} units"
                ),
                Formula(
                    name="COGS Calculation",
                    formula="COGS = Price per Unit × 25%",
                    calculation=f"€{price_per_unit} × 25% = €{cogs_per_unit:.2f}"
                ),
                Formula(
                    name="Net Profit Calculation",
                    formula="Net Profit = Total Revenue - (COGS + Operations + Marketing + Dev)",
                    calculation=f"€{total_revenue:,.0f} - €{total_cost:,.0f} = €{net_profit:,.0f}"
                ),
                Formula(
                    name="ROI Calculation",
                    formula="ROI % = (Net Profit ÷ Total Cost) × 100",
                    calculation=f"(€{net_profit:,.0f} ÷ €{total_cost:,.0f}) × 100 = {roi_pct:.1f}%"
                ),
            ]
        
        return ComprehensiveAnalysis(
            project_name=project_name,
            project_type=project_type,
            tam=TAMMetrics(
                description_of_public=f"Total addressable savings opportunity for {project_name}" if is_savings else f"Total addressable market for {project_name}",
                market_size=tam,
                growth_rate=growth,
                numbers=tam_numbers,
                justification=f"Calculated from {'savings streams across 4 initiatives' if total_streams else 'annual savings potential'}",
                insight=f"Total savings potential: €{tam/1_000_000:.1f}M with {growth}% annual growth" if is_savings else f"Market size: €{tam/1_000_000:.1f}M with {growth}% annual growth",
                confidence=85
            ),
            sam=SAMMetrics(
                description_of_public=f"Serviceable savings ({sam_percent}% of TAM) - organizational capacity" if is_savings else f"Serviceable available market ({sam_percent}% of TAM)",
                market_size=sam,
                numbers=sam_numbers,
                justification=f"Limited by budget, resources, and change management capacity" if is_savings else f"Full internal access: {sam_percent}% penetration",
                insight=f"Achievable savings considering organizational constraints: €{sam/1_000_000:.1f}M" if is_savings else f"Realistic serviceable market of €{sam/1_000_000:.1f}M",
                confidence=80,
                penetration_rate=sam_percent
            ),
            som=SOMMetrics(
                description_of_public=f"Obtainable savings ({som_percent}% of SAM) - execution realism" if is_savings else f"Serviceable obtainable market ({som_percent}% of SAM)",
                market_share=som_percent,
                revenue_potential=som,
                numbers=som_numbers,
                justification=f"Accounts for implementation challenges and adoption resistance" if is_savings else f"Target {som_percent}% implementation rate",
                insight=f"Realistic net savings after execution risk: €{som/1_000_000:.1f}M" if is_savings else f"Achievable revenue potential: €{som/1_000_000:.1f}M",
                confidence=75,
                customer_acquisition_cost=0
            ),
            roi=ROIMetrics(
                revenue=total_revenue,
                cost=total_cost,
                roi_percentage=roi_pct,
                numbers=roi_numbers,
                payback_period_months=break_even_months,
                insight=f"ROI: {roi_pct:.1f}% over 5 years, break-even in {break_even_months} months",
                confidence=80
            ),
            turnover=TurnoverMetrics(
                total_revenue=total_revenue / 5,
                yoy_growth=growth,
                numbers=yearly_revenue,
                insight=f"Average annual revenue: €{total_revenue/5/1_000_000:.1f}M",
                confidence=75
            ),
            volume=VolumeMetrics(
                units_sold=int(round(units)),  # Convert float to integer
                numbers=volume_numbers,
                insight=f"Projected volume: {int(units):,} units in year 1" if not is_savings else "Savings project - no unit volume",
                confidence=70
            ),
            unit_economics=UnitEconomics(
                unit_revenue=price_per_unit,
                unit_cost=cogs_per_unit,
                margin=price_per_unit - cogs_per_unit if not is_savings else 0,
                margin_percentage=profit_margin,
                ltv_cac_ratio=5.0,
                insight=f"Profit margin: {profit_margin:.1f}%" if not is_savings else f"Savings efficiency: {profit_margin:.1f}%",
                confidence=75
            ),
            ebit=EBITMetrics(
                revenue=total_revenue / 5,
                operating_expense=total_cost / 5,
                ebit_margin=net_profit / 5,
                ebit_percentage=profit_margin,
                numbers=ebit_numbers,
                insight=f"EBIT margin: {profit_margin:.1f}%",
                confidence=75
            ),
            cogs=COGSMetrics(
                material=0,
                labor=0,
                overheads=0,
                total_cogs=cogs_per_unit * units,
                cogs_percentage=(cogs_per_unit / price_per_unit * 100) if price_per_unit > 0 else 25,
                numbers={str(y): yearly_costs[str(y)]['total_cogs'] for y in years},
                insight=f"COGS per unit: €{cogs_per_unit:.2f}",
                confidence=70
            ),
            market_potential=MarketPotential(
                market_size=tam,
                penetration=som_percent,
                growth_rate=growth,
                numbers=tam_numbers,
                insight=f"Strong market potential with {growth}% growth",
                confidence=80
            ),
            yearly_cost_breakdown=yearly_costs,
            seven_year_summary={
                'total_cost_2024_2030': total_cost,
                'total_volume_2024_2030': int(total_volume),
                'average_cost_per_unit': total_cost / total_volume if total_volume > 0 else 0,
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
            executive_summary=f"{project_name}: €{tam/1_000_000:.1f}M total savings potential, €{som/1_000_000:.1f}M achievable savings, {roi_pct:.1f}% ROI over 5 years." if is_savings else f"{project_name}: €{tam/1_000_000:.1f}M TAM, €{som/1_000_000:.1f}M SOM, {roi_pct:.1f}% ROI over 5 years.",
            value_market_potential_text=f"Strong savings opportunity with €{tam/1_000_000:.1f}M total potential and {growth}% annual growth. Target achievable savings of €{som/1_000_000:.1f}M represents {som_percent}% execution rate with {roi_pct:.1f}% ROI and {break_even_months} months to break-even. Implementation requires €{dev_cost/1_000_000:.1f}M upfront investment." if is_savings else f"Strong market opportunity with €{tam/1_000_000:.1f}M TAM and {growth}% annual growth. Target SOM of €{som/1_000_000:.1f}M represents {som_percent}% market penetration with {roi_pct:.1f}% ROI and {break_even_months} months to break-even.",
            business_assumptions=[
                f"{growth}% annual growth rate",
                f"{som_percent}% implementation penetration target" if is_savings else f"{som_percent}% market penetration target",
                f"Annual savings: €{som/5:,.0f} (Year 1)" if is_savings else f"€{price_per_unit:.0f} average transaction value"
            ],
            improvement_recommendations=[
                "Pilot highest-value stream first to validate savings assumptions",
                "Establish clear KPIs and tracking mechanisms for each stream",
                "Secure executive sponsorship for organizational change management",
                "Plan phased rollout to manage implementation risk"
            ] if is_savings else [
                "Validate price elasticity with market research",
                "Monitor competitor pricing and adjust strategy",
                "Optimize unit economics to improve margins"
            ],
            identified_variables=identified_vars,
            formulas=formulas
        )
        
    except Exception as e:
        print(f"\n❌ CALCULATOR ERROR:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        raise
