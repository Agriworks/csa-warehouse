"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import { fetchDashboards, type DashboardInfo } from "@/lib/dashboard-api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Loader2,
  ExternalLink,
  Activity,
  PhoneCall,
  Users,
  BarChart2,
  ShoppingCart,
  Package,
  TrendingUp,
  LayoutDashboard,
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

// ─── Per-dashboard metadata ───────────────────────────────────────────────────
// Key = the slug from mount_path (e.g. "kisan_mitra" from "/dashboard/kisan_mitra")
// Add a new entry here whenever a new dashboard is added to the backend.
const DASHBOARD_META: Record<
  string,
  { description: string; icon: React.ElementType; color: string }
> = {
  kisan_mitra: {
    description:
      "Helpline case tracking — resolution rates, aging analysis, district & department breakdown.",
    icon: PhoneCall,
    color: "text-emerald-600",
  },
  nf_coordinator_dashboard: {
    description:
      "NF Coordinator performance — planned vs actual activities, score trends by month and coordinator.",
    icon: Users,
    color: "text-blue-600",
  },
  purchase_sales_dashboard: {
    description:
      "Territory-wise purchase & sales analysis — total amounts, net position, and monthly purchase vs sales trends.",
    icon: ShoppingCart,
    color: "text-orange-600",
  },
  farmer_income_dashboard: {
    description:
      "Farmer income tracking, total farmers met, total coordinator visits, and performance by village and coordinator.",
    icon: BarChart2,
    color: "text-purple-600",
  },
  stock_movement_dashboard: {
    description:
      "Stock inventory tracking — Net stock movement, Sum of In/Out quantity, and balance values by year.",
    icon: Package,
    color: "text-amber-600",
  },
  stock_inventory_dashboard: {
    description:
      "Comprehensive warehouse inventory monitoring — Total stock quantity, value, items in stock, and warehouse totals.",
    icon: TrendingUp,
    color: "text-rose-600",
  },
  revenue_analysis_dashboard: {
    description:
      "Detailed financial analysis — Avg monthly purchase, sales, profit margin, net revenue by territory and monthly trends.",
    icon: TrendingUp,
    color: "text-indigo-600",
  },
  // ── add future dashboards below ───────────────────────────────────────────
};

/** Fallback meta for any dashboard not yet listed above */
const DEFAULT_META = {
  description: "Interactive analytics dashboard.",
  icon: LayoutDashboard,
  color: "text-slate-500",
};

function getDashboardMeta(mountPath: string) {
  const slug = mountPath.replace("/dashboard/", "");
  return DASHBOARD_META[slug] ?? DEFAULT_META;
}
// ─────────────────────────────────────────────────────────────────────────────

export default function DashboardsPage() {
  const [dashboards, setDashboards] = useState<DashboardInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { data: session } = useSession();
  const router = useRouter();

  useEffect(() => {
    const loadDashboards = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchDashboards(session?.user?.apiToken);
        setDashboards(response.dashboards || []);
      } catch (err) {
        console.error("Failed to fetch dashboards:", err);
        setError(
          err instanceof Error ? err.message : "Failed to load dashboards"
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboards();
  }, [session?.user?.apiToken]);

  const handleDashboardClick = (dashboard: DashboardInfo) => {
    const dashboardName = dashboard.mount_path.replace("/dashboard/", "");
    if (dashboardName) {
      router.push(`/dashboard/${dashboardName}`);
    }
  };

  if (loading) {
    return (
      <ContentLayout title="Dashboards">
        <div className="flex items-center justify-center h-full">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </ContentLayout>
    );
  }

  if (error) {
    return (
      <ContentLayout title="Dashboards">
        <div className="container mx-auto p-6">
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </ContentLayout>
    );
  }

  return (
    <ContentLayout title="Dashboards">
      <div className="container mx-auto p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold mb-2">Available Dashboards</h2>
          <p className="text-muted-foreground">
            {dashboards.length === 0
              ? "No dashboards available"
              : `${dashboards.length} dashboard${
                  dashboards.length !== 1 ? "s" : ""
                } available`}
          </p>
        </div>

        {dashboards.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-muted-foreground">
                No dashboards are currently available. Check back later or
                contact your administrator.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboards.map((dashboard) => {
              const meta = getDashboardMeta(dashboard.mount_path);
              const Icon = meta.icon;
              return (
                <Card
                  key={dashboard.mount_path}
                  className="cursor-pointer hover:shadow-lg transition-shadow flex flex-col"
                  onClick={() => handleDashboardClick(dashboard)}
                >
                  <CardHeader className="flex-shrink-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <Icon className={`h-5 w-5 flex-shrink-0 ${meta.color}`} />
                        <CardTitle className="text-lg truncate">
                          {dashboard.name}
                        </CardTitle>
                      </div>
                      <Badge
                        variant="outline"
                        className="capitalize flex-shrink-0"
                      >
                        <Activity className="h-3 w-3 mr-1" />
                        {dashboard.status}
                      </Badge>
                    </div>
                    <CardDescription className="mt-2 line-clamp-2">
                      {meta.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col justify-between gap-3">
                    <span className="text-xs text-muted-foreground font-mono truncate">
                      {dashboard.mount_path} · port {dashboard.port}
                    </span>
                    <Button
                      size="sm"
                      variant="outline"
                      className="w-full"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDashboardClick(dashboard);
                      }}
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Open Dashboard
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </ContentLayout>
  );
}
