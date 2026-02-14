"""ロールベースアクセス制御 (RBAC) を実装した MCP ツール。

このモジュールは、アクセストークンの roles クレームに基づいて、
返却する情報を制御します。異なるロールに応じて、異なるレベルの
情報へのアクセスを許可します。
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastmcp import FastMCP
from starlette.authentication import AuthenticationError

from auth.claims_helpers import get_user_context, has_role

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """ロールベースアクセス制御ツールを FastMCP に登録する。"""

    @mcp.tool()
    async def get_company_info() -> Dict[str, Any]:
        """企業情報を取得します。ロールに応じて返される情報が変わります。

        - Admin ロール: 機密情報を含むすべての情報にアクセス可能
        - Auditor ロール: 監査情報と基本情報にアクセス可能
        - User ロール: 基本的な公開情報のみにアクセス可能
        - ロールなし: 限定的な公開情報のみ

        返却される情報:
        - 公開情報: 会社名、設立年、公開連絡先など
        - 監査情報: 従業員数、年間売上、監査レポートなど
        - 機密情報: 未公開プロジェクト、財務詳細、経営戦略など
        """
        roles, user_id, client_id, scopes, _ = get_user_context()

        logger.debug(
            "get_company_info invoked: user=%s client=%s roles=%s scopes=%s",
            user_id,
            client_id,
            roles,
            scopes,
        )

        # 基本的な公開情報 (すべてのユーザーに提供)
        result: Dict[str, Any] = {
            "access_level": "public",
            "user_roles": roles,
            "company_name": "Contoso Corporation",
            "founded_year": 1995,
            "public_contact": {
                "email": "info@contoso.com",
                "phone": "+1-555-0100",
                "website": "https://www.contoso.com",
            },
            "headquarters": "Seattle, WA, USA",
            "industry": "Technology",
        }

        # User ロールまたは何らかのロールがある場合は、より詳細な公開情報を追加
        if roles:
            result["access_level"] = "user"
            result["public_info"] = {
                "employee_count_range": "1000-5000",
                "stock_symbol": "CTSO",
                "description": "Leading provider of cloud-based business solutions",
                "certifications": ["ISO 27001", "SOC 2 Type II"],
            }

        # Auditor ロールがある場合は、監査情報を追加
        if has_role(roles, "Auditor") or has_role(roles, "Admin"):
            result["access_level"] = "auditor"
            result["audit_info"] = {
                "employee_count": 2847,
                "annual_revenue_usd": 450_000_000,
                "fiscal_year_end": "2025-12-31",
                "audit_firm": "Big Four Accounting LLP",
                "last_audit_date": "2025-01-15",
                "compliance_status": "Fully Compliant",
                "audit_reports": [
                    {
                        "year": 2024,
                        "status": "Clean Opinion",
                        "date": "2025-01-15",
                    },
                    {
                        "year": 2023,
                        "status": "Clean Opinion",
                        "date": "2024-01-20",
                    },
                ],
            }

        # Admin ロールがある場合は、機密情報を追加
        if has_role(roles, "Admin"):
            result["access_level"] = "admin"
            result["confidential_info"] = {
                "unreleased_projects": [
                    {
                        "code_name": "Project Phoenix",
                        "description": "Next generation AI platform",
                        "expected_launch": "Q3 2026",
                        "budget_usd": 15_000_000,
                    },
                    {
                        "code_name": "Project Horizon",
                        "description": "Quantum computing initiative",
                        "expected_launch": "Q1 2027",
                        "budget_usd": 25_000_000,
                    },
                ],
                "financial_details": {
                    "actual_revenue_usd": 453_728_942,
                    "ebitda_usd": 89_456_231,
                    "cash_reserves_usd": 127_500_000,
                    "debt_usd": 45_000_000,
                    "quarterly_growth_rate": 0.078,
                },
                "strategic_plans": {
                    "market_expansion": [
                        "Southeast Asia",
                        "Latin America",
                        "Middle East",
                    ],
                    "acquisition_targets": [
                        "CloudSecure Technologies",
                        "DataViz Analytics",
                    ],
                    "planned_headcount_increase": 450,
                },
                "executive_compensation": {
                    "ceo_total_compensation_usd": 2_500_000,
                    "cto_total_compensation_usd": 1_800_000,
                    "cfo_total_compensation_usd": 1_750_000,
                },
            }
            logger.info("Confidential information accessed by Admin user: %s", user_id)

        logger.info(
            "Company info returned with access level '%s' for user %s with roles %s",
            result["access_level"],
            user_id,
            roles,
        )

        return result

    @mcp.tool()
    async def get_sensitive_data() -> Dict[str, Any]:
        """Admin ロールが必要な機密データを取得します。

        例外:
            AuthenticationError: Admin ロールを持っていない場合

        このツールは、Admin ロールを持つユーザーのみがアクセスできる
        機密データのサンプルを返します。実際の使用では、データベースや
        外部 API から取得したデータを返すことができます。
        """
        roles, user_id, _, scopes, _ = get_user_context()
        required_role = "Admin"

        logger.debug(
            "get_sensitive_data invoked: user=%s user_roles=%s scopes=%s",
            user_id,
            roles,
            scopes,
        )

        # Admin ロールを持っているか確認
        if not has_role(roles, required_role):
            logger.warning(
                "Access denied: user %s with roles %s tried to access Admin-only data",
                user_id,
                roles,
            )
            raise AuthenticationError(
                f"insufficient_role: 'Admin' role required, but user has {roles}"
            )

        # Admin ロールを持っている場合は、機密データを返す
        logger.info(
            "Sensitive data accessed by Admin user %s",
            user_id,
        )

        return {
            "status": "success",
            "required_role": "Admin",
            "user_roles": roles,
            "data": {
                "sensitive_documents": [
                    {
                        "id": "DOC-2025-001",
                        "title": "Q4 2025 Financial Projections",
                        "classification": "Confidential",
                        "created_date": "2025-01-10",
                    },
                    {
                        "id": "DOC-2025-002",
                        "title": "M&A Strategy Document",
                        "classification": "Top Secret",
                        "created_date": "2025-01-25",
                    },
                ],
                "access_granted_at": "2026-02-14T00:00:00Z",
                "access_granted_to": user_id,
            },
        }

    @mcp.tool()
    async def list_available_resources() -> Dict[str, Any]:
        """現在のユーザーのロールでアクセス可能なリソースを一覧表示します。

        このツールは、ユーザーが持つロールに基づいて、アクセス可能な
        リソースとアクションをリストアップします。これにより、ユーザーは
        自分がアクセスできる情報を事前に把握できます。
        """
        roles, user_id, _, scopes, claims = get_user_context()
        user_name = claims.get("name") or claims.get("upn")

        logger.debug(
            "list_available_resources invoked: user=%s roles=%s scopes=%s",
            user_id,
            roles,
            scopes,
        )

        # すべてのユーザーがアクセスできる基本リソース
        available_resources = {
            "user_info": {
                "name": user_name,
                "user_id": user_id,
                "roles": roles,
            },
            "accessible_resources": [
                {
                    "resource": "公開会社情報",
                    "description": "会社の基本的な公開情報",
                    "access_level": "public",
                    "tools": ["get_company_info"],
                },
            ],
        }

        # User ロール以上の場合
        if roles:
            available_resources["accessible_resources"].extend(
                [
                    {
                        "resource": "詳細な公開情報",
                        "description": "従業員数範囲、認証情報など",
                        "access_level": "user",
                        "tools": ["get_company_info"],
                    },
                ]
            )

        # Auditor ロールを持つ場合
        if has_role(roles, "Auditor"):
            available_resources["accessible_resources"].extend(
                [
                    {
                        "resource": "監査情報",
                        "description": "財務監査、コンプライアンス情報",
                        "access_level": "auditor",
                        "tools": ["get_company_info"],
                    },
                ]
            )

        # Admin ロールを持つ場合
        if has_role(roles, "Admin"):
            available_resources["accessible_resources"].extend(
                [
                    {
                        "resource": "機密情報",
                        "description": "未公開プロジェクト、詳細財務情報、戦略計画",
                        "access_level": "admin",
                        "tools": ["get_company_info", "get_sensitive_data"],
                    },
                    {
                        "resource": "役員報酬情報",
                        "description": "経営陣の報酬情報",
                        "access_level": "admin",
                        "tools": ["get_company_info"],
                    },
                ]
            )

        logger.info(
            "Listed %d accessible resources for user %s with roles %s",
            len(available_resources["accessible_resources"]),
            user_id,
            roles,
        )

        return available_resources
