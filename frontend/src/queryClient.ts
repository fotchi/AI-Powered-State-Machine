import { QueryClient } from "@tanstack/react-query";

// Cache client partagé pour toutes les données API -- remplace les
// useEffect+fetch répétés dans chaque écran. staleTime raisonnable car
// les scénarios/scripts ne changent qu'après une génération explicite,
// pas en continu.
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // 30s -- évite un refetch à chaque changement d'écran
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});