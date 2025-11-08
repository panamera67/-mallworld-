import { useEffect, useState } from "react";
import { collection, getDocs, query, where } from "firebase/firestore";
import { db } from "../lib/firebase";

export default function useMallEvents(mallName) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!mallName) {
      setEvents([]);
      return;
    }

    let isSubscribed = true;

    async function fetchEvents() {
      setLoading(true);
      setError(null);

      try {
        const eventsQuery = query(
          collection(db, "mall_events"),
          where("mall", "==", mallName)
        );
        const snapshot = await getDocs(eventsQuery);

        if (!isSubscribed) return;

        const data = snapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        }));

        setEvents(data);
      } catch (err) {
        if (isSubscribed) {
          console.error("Erreur lors de la récupération des événements:", err);
          setError(err);
          setEvents([]);
        }
      } finally {
        if (isSubscribed) {
          setLoading(false);
        }
      }
    }

    fetchEvents();

    return () => {
      isSubscribed = false;
    };
  }, [mallName]);

  return { events, loading, error };
}
