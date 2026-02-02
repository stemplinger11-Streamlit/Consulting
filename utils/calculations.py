"""
Sizing and Calculation Functions
"""

import streamlit as st
from typing import Dict, List, Tuple

class SizingCalculator:
    """Calculate sizing recommendations for network deployments"""
    
    @staticmethod
    def calculate_ap_requirements(
        area_sqm: float,
        client_count: int,
        deployment_type: str = "Office",
        high_density: bool = False
    ) -> Dict:
        """
        Calculate Access Point requirements
        
        Returns:
        {
            'recommended_aps': int,
            'ap_model_suggestions': List[str],
            'reasoning': str
        }
        """
        # Coverage area per AP based on deployment type
        coverage_per_ap = {
            "Office": 200,
            "Warehouse": 350,
            "Hospital": 150,
            "School": 180,
            "Retail": 160,
            "Stadium": 100
        }
        
        base_coverage = coverage_per_ap.get(deployment_type, 200)
        
        # Calculate based on area
        aps_by_area = int(area_sqm / base_coverage) + 1
        
        # Calculate based on client density (max 100 clients per AP for normal, 200 for high-density)
        max_clients_per_ap = 200 if high_density else 100
        aps_by_clients = int(client_count / max_clients_per_ap) + 1
        
        # Take the maximum
        recommended_aps = max(aps_by_area, aps_by_clients)
        
        # Suggest AP models
        if high_density:
            suggestions = ["MR46", "MR56", "MR57", "C9124AXI", "C9164I"]
        elif client_count / recommended_aps > 50:
            suggestions = ["MR36", "MR46", "C9120AXI"]
        else:
            suggestions = ["MR28", "MR36", "C9115AXI"]
        
        reasoning = f"Basierend auf {area_sqm:.0f}m² Fläche und {client_count} Clients: "
        reasoning += f"{aps_by_area} APs für Flächenabdeckung, {aps_by_clients} APs für Client-Kapazität."
        
        return {
            'recommended_aps': recommended_aps,
            'ap_model_suggestions': suggestions,
            'reasoning': reasoning
        }
    
    @staticmethod
    def calculate_firewall_requirements(
        user_count: int,
        bandwidth_mbps: int,
        vpn_tunnels: int = 0,
        advanced_security: bool = True
    ) -> Dict:
        """
        Calculate Firewall (MX) requirements
        
        Returns:
        {
            'recommended_models': List[str],
            'ha_recommended': bool,
            'reasoning': str
        }
        """
        bandwidth_gbps = bandwidth_mbps / 1000
        
        # Base recommendations
        if user_count <= 50 and bandwidth_gbps <= 0.5:
            models = ["MX67", "MX68"]
        elif user_count <= 200 and bandwidth_gbps <= 1:
            models = ["MX75"]
        elif user_count <= 250 and bandwidth_gbps <= 1:
            models = ["MX85"]
        elif user_count <= 500 and bandwidth_gbps <= 2.5:
            models = ["MX95"]
        elif user_count <= 2000:
            models = ["MX250"]
        else:
            models = ["MX450"]
        
        # Adjust for VPN tunnels
        if vpn_tunnels > 100:
            if "MX67" in models or "MX68" in models:
                models = ["MX75", "MX85"]
            if vpn_tunnels > 250:
                models = ["MX95", "MX250"]
        
        # HA recommendation
        ha_recommended = user_count > 100 or vpn_tunnels > 50
        
        reasoning = f"Für {user_count} User, {bandwidth_gbps:.1f} Gbps Throughput"
        if vpn_tunnels > 0:
            reasoning += f" und {vpn_tunnels} VPN Tunnel"
        reasoning += ". "
        
        if ha_recommended:
            reasoning += "HA-Paar wird empfohlen für Redundanz."
        
        return {
            'recommended_models': models,
            'ha_recommended': ha_recommended,
            'reasoning': reasoning
        }
    
    @staticmethod
    def calculate_switch_requirements(
        access_ports_needed: int,
        poe_devices: int,
        upoe_devices: int = 0,
        stacking_required: bool = False
    ) -> Dict:
        """
        Calculate Switch requirements
        
        Returns:
        {
            'recommended_switches': List[Dict],
            'total_poe_budget_needed': int,
            'reasoning': str
        }
        """
        # Calculate PoE budget needed
        poe_budget_needed = (poe_devices * 30) + (upoe_devices * 60)  # PoE+ = 30W, UPOE = 60W
        
        switches = []
        
        # Determine switch models
        if access_ports_needed <= 8:
            if poe_devices > 0:
                switches.append({'model': 'MS120-8FP', 'quantity': 1})
            else:
                switches.append({'model': 'MS120-8', 'quantity': 1})
        
        elif access_ports_needed <= 24:
            if upoe_devices > 0:
                switches.append({'model': 'MS350-24X', 'quantity': 1})
            elif poe_devices > 0:
                switches.append({'model': 'MS120-24P', 'quantity': 1})
            else:
                switches.append({'model': 'MS120-24', 'quantity': 1})
        
        elif access_ports_needed <= 48:
            if upoe_devices > 0:
                switches.append({'model': 'MS350-24X', 'quantity': 2})
            elif poe_devices > 0:
                switches.append({'model': 'MS225-48FP', 'quantity': 1})
            else:
                switches.append({'model': 'MS225-48', 'quantity': 1})
        
        else:
            # Multiple switches needed
            num_48port = int(access_ports_needed / 48) + 1
            if poe_budget_needed > 740 * num_48port:
                switches.append({'model': 'MS350-24X', 'quantity': num_48port})
            elif poe_devices > 0:
                switches.append({'model': 'MS225-48FP', 'quantity': num_48port})
            else:
                switches.append({'model': 'MS225-48', 'quantity': num_48port})
        
        # Add aggregation/core if stacking
        if stacking_required and len(switches) > 0 and switches[0]['quantity'] > 1:
            switches.append({'model': 'MA-CBL-40G-2M', 'quantity': switches[0]['quantity'] - 1, 'type': 'stacking_cable'})
        
        reasoning = f"{access_ports_needed} Access-Ports benötigt, davon {poe_devices} PoE+ und {upoe_devices} UPOE. "
        reasoning += f"Gesamt PoE-Budget: {poe_budget_needed}W."
        
        return {
            'recommended_switches': switches,
            'total_poe_budget_needed': poe_budget_needed,
            'reasoning': reasoning
        }
    
    @staticmethod
    def calculate_ise_requirements(
        endpoint_count: int,
        concurrent_sessions: int,
        deployment_scenario: str = "Single Site"
    ) -> Dict:
        """
        Calculate ISE requirements
        
        Returns:
        {
            'recommended_model': str,
            'node_count': int,
            'deployment_architecture': str,
            'reasoning': str
        }
        """
        # Single appliance sizing
        if endpoint_count <= 5000:
            model = "ISE-3315"
        elif endpoint_count <= 50000:
            model = "ISE-3355"
        elif endpoint_count <= 100000:
            model = "ISE-3395"
        elif endpoint_count <= 200000:
            model = "ISE-3415"
        else:
            model = "ISE-3495"
        
        # Distributed deployment
        if deployment_scenario == "Distributed Multi-Site":
            node_count = max(2, int(endpoint_count / 50000) + 1)
            architecture = "Distributed (2x PAN, 2x MnT, Nx PSN)"
        elif deployment_scenario == "High Availability":
            node_count = 2
            architecture = "HA Pair (Active-Standby PAN/MnT/PSN)"
        else:
            node_count = 1
            architecture = "Standalone"
        
        reasoning = f"{endpoint_count:,} Endpoints, {concurrent_sessions:,} gleichzeitige Sessions. "
        reasoning += f"{deployment_scenario}-Szenario empfiehlt {architecture}."
        
        return {
            'recommended_model': model,
            'node_count': node_count,
            'deployment_architecture': architecture,
            'reasoning': reasoning
        }

