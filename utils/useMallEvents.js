import { useEffect, useState } from "react";
import {
  collection,
  onSnapshot,
  query,
  where,
} from "firebase/firestore";
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

    setLoading(true);
    setError(null);

    const eventsQuery = query(
      collection(db, "mall_events"),
      where("mall", "==", mallName)
    );

    const unsubscribe = onSnapshot(
      eventsQuery,
      (snapshot) => {
        const data = snapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        }));
        setEvents(data);
        setLoading(false);
      },
      (err) => {
        console.error("Erreur lors de la récupération des événements:", err);
        setError(err);
        setEvents([]);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [mallName]);

  return { events, loading, error };
}
